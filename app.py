import os
import uuid
import base64
import sqlite3
import cv2
import numpy as np
import datetime
from dotenv import load_dotenv

from flask import (
    Flask, request, render_template,
    redirect, url_for, session, flash, g, jsonify
)

# -- LOGIN CODE
from flask_bcrypt import Bcrypt
from datetime import timedelta

###############################################################################
# CONFIG & INIT
###############################################################################

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH_MB', 10)) * 1024 * 1024  # MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -- LOGIN CODE
app.permanent_session_lifetime = timedelta(weeks=1)  # Remember login for 1 week

bcrypt = Bcrypt(app)

# Load allowed user credentials from environment
ALLOWED_USERNAME = os.getenv('ALLOWED_USERNAME', 'defaultuser')
ALLOWED_PASSWORD = os.getenv('ALLOWED_PASSWORD', 'defaultpass')
ALLOWED_PASSWORD_HASH = bcrypt.generate_password_hash(ALLOWED_PASSWORD).decode('utf-8')

MAX_LOGIN_TRIES = int(os.getenv('MAX_LOGIN_TRIES', 5))
LOCKOUT_MINUTES = int(os.getenv('LOCKOUT_MINUTES', 15))

DB_PATH = os.getenv('DB_PATH', 'database/items.db')
os.makedirs('database', exist_ok=True)
ORB = cv2.ORB_create()

def get_db():
    """Get or create a database connection, store it in flask.g."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close DB connection after request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database schema for items and images."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL
        );
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            descriptor BLOB,
            FOREIGN KEY(item_id) REFERENCES items(id)
        );
    ''')
    conn.commit()
    conn.close()

###############################################################################
# UTILS
###############################################################################

def is_blurry_cv2_image(cv2_img, threshold=80.0):
    """Return True if cv2_img (grayscale) is considered blurry using Laplacian."""
    if cv2_img is None:
        return True
    laplacian_var = cv2.Laplacian(cv2_img, cv2.CV_64F).var()
    return laplacian_var < threshold


def compute_descriptor_cv2_image(cv2_img):
    """Compute ORB descriptor for a cv2 grayscale image in memory."""
    if cv2_img is None:
        return None
    keypoints, descriptor = ORB.detectAndCompute(cv2_img, None)
    return descriptor


def save_descriptor_to_db(img_id, descriptor):
    """Save descriptor bytes to the 'images' table for a given image row."""
    if descriptor is None:
        return
    descriptor_bytes = descriptor.tobytes()
    conn = get_db()
    conn.execute(
        "UPDATE images SET descriptor = ? WHERE id = ?",
        (descriptor_bytes, img_id)
    )
    conn.commit()


def load_descriptor_from_db(descriptor_blob, shape=(-1, 32)):
    """Convert a BLOB (bytes) back into a numpy array of shape (N, 32)."""
    if descriptor_blob is None:
        return None
    arr = np.frombuffer(descriptor_blob, dtype=np.uint8)
    if shape[0] == -1:
        arr = arr.reshape((-1, 32))
    else:
        arr = arr.reshape(shape)
    return arr


def match_search_against_item(search_desc, item_id):
    """
    Compare a search descriptor against ALL images for an item.
    Return the best match score among that item's images.
    """
    if search_desc is None:
        return 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    conn = get_db()
    images_rows = conn.execute(
        "SELECT descriptor FROM images WHERE item_id = ?",
        (item_id,)
    ).fetchall()

    best_score = 0
    for (desc_blob,) in images_rows:
        db_desc = load_descriptor_from_db(desc_blob)
        if db_desc is None:
            continue
        matches = bf.match(search_desc, db_desc)
        # Slightly looser distance threshold for better mobile recognition
        good_matches = [m for m in matches if m.distance < 55]
        score = len(good_matches)
        if score > best_score:
            best_score = score
    return best_score


def best_item_match_descriptor(search_desc):
    """
    Compare the search_desc with all items in DB.
    Return (best_item_id, best_score).
    """
    if search_desc is None:
        return (None, 0)

    conn = get_db()
    items = conn.execute("SELECT id FROM items").fetchall()

    best_item_id = None
    best_score = 0

    for (item_id,) in items:
        score = match_search_against_item(search_desc, item_id)
        if score > best_score:
            best_score = score
            best_item_id = item_id

    return (best_item_id, best_score)


@app.after_request
def add_header(response):
    """Add headers to disable caching."""
    response.headers['Cache-Control'] = 'no-store'
    return response

###############################################################################
# LOGIN CODE
###############################################################################

def login_required(f):
    """
    Decorator to ensure the user is logged in before accessing certain routes.
    """
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    # For correct name in Flask’s routing
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Single-user login route.
    Uses session to track login tries and lockout time.
    """
    # If already logged in, go home
    if session.get('logged_in'):
        flash("You are already logged in.")
        return redirect(url_for('index'))

    # Check if locked out
    lockout_until = session.get('lockout_until')
    if lockout_until:
        now = datetime.datetime.now()
        if now < lockout_until:
            # Still locked out
            remaining = (lockout_until - now).seconds // 60
            flash(f"You are locked out. Please wait {remaining} more minutes.")
            return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Increment login tries
        session['login_tries'] = session.get('login_tries', 0) + 1

        # Compare with ALLOWED_USERNAME and hashed password
        if (username == ALLOWED_USERNAME and
            bcrypt.check_password_hash(ALLOWED_PASSWORD_HASH, password)):

            # Successful login
            session.permanent = True  # Make session last for app.permanent_session_lifetime
            session['logged_in'] = True
            # Reset tries and lockout
            session.pop('login_tries', None)
            session.pop('lockout_until', None)
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            # Wrong credentials
            tries_left = MAX_LOGIN_TRIES - session['login_tries']
            if tries_left <= 0:
                # Lock out
                lockout_time = datetime.datetime.now() + datetime.timedelta(minutes=LOCKOUT_MINUTES)
                session['lockout_until'] = lockout_time
                flash("Too many failed attempts. You are locked out for 15 minutes.")
            else:
                flash(f"Invalid credentials. You have {tries_left} tries left.")

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Logout user by clearing session.
    """
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

###############################################################################
# ROUTES
###############################################################################

@app.route('/')
@login_required
def index():
    """Home: choose Add or View."""
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """
    1) GET -> Show form to get the URL for the new item.
    2) POST -> Create item in DB, store item_id in session,
               redirect to capturing 3 images.
    """
    if request.method == 'POST':
        url = request.form.get('itemURL')
        if not url:
            flash("URL is required.")
            return redirect(url_for('add_item'))

        # Insert item into DB
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO items (url) VALUES (?)", (url,))
        item_id = cur.lastrowid
        conn.commit()

        # Prepare to capture images
        session['new_item_id'] = item_id
        session['images_needed'] = 3
        return redirect(url_for('capture_images'))

    return render_template("add.html")


@app.route('/capture_images')
@login_required
def capture_images():
    """Displays the camera feed or file input to capture 'images_needed' times."""
    images_needed = session.get('images_needed', 3)
    # If no item in session, go back to add
    if 'new_item_id' not in session:
        flash("No item found in session. Please add an item first.")
        return redirect(url_for('add_item'))
    return render_template("capture_images.html", remaining=images_needed)


@app.route('/add_image', methods=['POST'])
@login_required
def add_image():
    """
    Handle each captured image (sent as multipart/form-data),
    check if blurry, store it, decrement images_needed.
    Once 3 images are captured, finalize and show add_success page.
    """
    img_file = request.files.get('image')
    item_id = session.get('new_item_id')

    if not img_file or not item_id:
        flash("Missing file or item_id. Please start over.")
        return redirect(url_for('index'))

    # Save uploaded image
    file_name = f"{uuid.uuid4()}.jpg"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    img_file.save(save_path)

    # Check for blur
    img_cv2 = cv2.imread(save_path, cv2.IMREAD_GRAYSCALE)
    if is_blurry_cv2_image(img_cv2, threshold=80.0):
        os.remove(save_path)  # Remove blurry image
        flash("That image was too blurry. Please capture again.")
        return jsonify({"error": "Image is blurry"}), 400

    # Insert into images table
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO images (item_id, image_path, descriptor) VALUES (?, ?, ?)",
        (item_id, save_path, None)
    )
    image_id = cur.lastrowid
    conn.commit()

    # Compute descriptor & store
    desc = compute_descriptor_cv2_image(img_cv2)
    save_descriptor_to_db(image_id, desc)

    # Decrement images needed
    session['images_needed'] = session.get('images_needed', 3) - 1
    if session['images_needed'] > 0:
        return jsonify({
            "success": True,
            "message": f"Image captured. {session['images_needed']} more to go."
        })
    else:
        # Done capturing
        session.pop('images_needed', None)
        session.pop('new_item_id', None)
        return jsonify({
            "success": True,
            "message": "All images captured successfully."
        })


@app.route('/view', methods=['GET', 'POST'])
@login_required
def view_item():
    """
    GET -> Show camera/file input to capture a photo and attempt recognition.
    POST -> Attempt recognition:
            - High confidence => show recognized.html
            - Borderline => ask user to add more images
            - Low match => "Not recognized"
    """
    if request.method == 'POST':
        data = request.get_json()
        img_data = data.get("imgData")
        if not img_data:
            return jsonify({"error": "No image data received."}), 400

        # Convert Base64 image to OpenCV format
        try:
            img_bytes = base64.b64decode(img_data.split(',')[1])
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img_cv2 = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        except Exception:
            return jsonify({"error": "Invalid image data."}), 400

        # Check if the image is blurry
        if is_blurry_cv2_image(img_cv2, threshold=80.0):
            return jsonify({"error": "Image is too blurry. Try again."}), 400

        # Compute descriptor
        search_desc = compute_descriptor_cv2_image(img_cv2)
        best_item_id, best_score = best_item_match_descriptor(search_desc)

        if not best_item_id:
            return jsonify({"error": "No match found."}), 404

        # Threshold logic
        HIGH_CONFIDENCE_THRESHOLD = 30
        BORDERLINE_THRESHOLD = 15

        if best_score >= HIGH_CONFIDENCE_THRESHOLD:
            conn = get_db()
            row = conn.execute(
                "SELECT url FROM items WHERE id = ?", (best_item_id,)
            ).fetchone()

            if row:
                url = row[0]
                if not url.startswith("http"):
                    url = "https://" + url
                return jsonify({"redirectUrl": url})
            return jsonify({"error": "Matched item URL not found."}), 500

        elif best_score >= BORDERLINE_THRESHOLD:
            return jsonify({"borderline": True})

        return jsonify({"error": "Item not recognized."}), 404

    # GET request -> Show camera/file input preview
    return render_template("view.html")


###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    init_db()
    # If you have actual certs, set them here; else remove ssl_context
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 443)), debug=bool(int(os.getenv('DEBUG', 1))))


Image Recognition (Flask + OpenCV + SQLite)

A simple Flask application for image-based item recognition, leveraging OpenCV's ORB feature descriptor and a SQLite database for storing items and their associated images.

🚀 Features

Item Management: CRUD operations for items with multiple images per item and a reference URL.

Image Processing:

Blurriness check to ensure image clarity.

ORB descriptors for reliable feature matching.

Recognition System:

Compares new image descriptors against stored items.

Threshold-based classification: high confidence, borderline, or no match.

User Interface:

Capture images via webcam or upload from desktop/mobile.

Authentication:

Single-user login with hashed passwords (bcrypt).

Session-based authentication and configurable lockout after failed attempts.

🛠️ Tech Stack

Backend: Python (Flask)

Image Processing: OpenCV

Database: SQLite

Frontend: JavaScript, HTML/CSS, Jinja2

📂 Table of Contents

Features

Tech Stack

Getting Started

Clone the Repo

Install Dependencies

Environment Variables

Run the Application

How It Works

Item Addition Workflow

Recognition Workflow

Project Structure

Contributing

License

Author

🏁 Getting Started

Clone the Repo

git clone https://github.com/Charisn/Image_recognition.git
cd Image_recognition

Install Dependencies

Ensure Python 3.8+ and pip are installed, then run:

pip install -r requirements.txt

If requirements.txt is missing, manually install key modules: flask, python-dotenv, opencv-python, numpy, bcrypt, etc.

Environment Variables

Create a .env file in the project root:

SECRET_KEY=some-random-key
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH_MB=10
ALLOWED_USERNAME=defaultuser
ALLOWED_PASSWORD=defaultpass
MAX_LOGIN_TRIES=5
LOCKOUT_MINUTES=15
DB_PATH=database/items.db
PORT=443
DEBUG=1

Note:

PORT=443 implies HTTPS. For HTTP (e.g., port 5000), adjust PORT accordingly.

On first run, the app auto-creates the database and uploads folders.

Run the Application

python app.py

Access the app at https://localhost:443 (or your configured host/port).

🔎 How It Works

Item Addition Workflow

Login: Go to /login and enter your credentials.

Add Item: Navigate to /add and submit the item's URL.

Capture Images: Provide 3 clear images:

Blurriness check (Laplacian variance).

ORB descriptors generated and stored.

Completion: After successful uploads, the item is ready for recognition.

Recognition Workflow

Navigate to /view.

Capture/Upload an image.

Processing:

Blurriness check.

ORB descriptor computation.

Descriptor comparison against stored items.

Results:

High confidence: Redirect to item URL.

Borderline: Prompt for more images.

No match: Notify the user.

📁 Project Structure

Image_recognition/
├── app.py                # Main Flask application
├── scripts.js            # Client-side camera handling
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── add.html
│   ├── capture_images.html
│   ├── view.html
├── static/
│   └── uploads/          # Stored captured images
├── database/
│   └── items.db          # SQLite database (auto-created)
├── .env                  # Environment config
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation

🤝 Contributing

Fork the repository

Create a feature branch

git checkout -b feature/new-stuff

Commit changes

git commit -m 'Add new feature'

Push to your branch

git push origin feature/new-stuff

Open a Pull Request

📜 License

This project is open-source. Feel free to modify and use it as needed. Check the LICENSE file for more details.

👤 Author

CharisnSenior Software Engineer passionate about solving problems and exploring new technologies.

Questions or ideas? Open an issue or submit a pull request!
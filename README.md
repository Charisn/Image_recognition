
# Image Recognition (Flask + OpenCV + SQLite)

A simple Flask application for image-based item recognition, leveraging OpenCV's ORB feature descriptor and a SQLite database for storing items and their associated images.

## 🚀 Features

### Item Management
- **CRUD Operations:** Manage items with Create, Read, Update, and Delete functionalities.
- **Multiple Images:** Associate multiple images per item.
- **Reference URL:** Link each item to a reference URL.

### Image Processing
- **Blurriness Check:** Ensure image clarity using Laplacian variance.
- **ORB Descriptors:** Utilize ORB feature descriptors for reliable feature matching.

### Recognition System
- **Descriptor Comparison:** Compare new image descriptors against stored items.
- **Threshold-Based Classification:**
  - **High Confidence:** Confident match found.
  - **Borderline:** Prompt for more images.
  - **No Match:** Notify the user of no match.

### User Interface
- **Image Capture:** Capture images via webcam or upload from desktop/mobile.

### Authentication
- **Single-User Login:** Secure login with hashed passwords (bcrypt).
- **Session Management:** Session-based authentication with configurable lockout after failed attempts.

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Image Processing:** OpenCV
- **Database:** SQLite
- **Frontend:** JavaScript, HTML/CSS, Jinja2

## 📂 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Clone the Repo](#clone-the-repo)
  - [Install Dependencies](#install-dependencies)
  - [Environment Variables](#environment-variables)
  - [Run the Application](#run-the-application)
- [How It Works](#-how-it-works)
  - [Item Addition Workflow](#item-addition-workflow)
  - [Recognition Workflow](#recognition-workflow)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## 🏁 Getting Started

### Clone the Repo

```bash
git clone https://github.com/Charisn/Image_recognition.git
cd Image_recognition
```

### Install Dependencies

Ensure Python 3.8+ and `pip` are installed, then run:

```bash
pip install -r requirements.txt
```

*If `requirements.txt` is missing, manually install key modules: `flask`, `python-dotenv`, `opencv-python`, `numpy`, `bcrypt`, etc.*

### Environment Variables

Create a `.env` file in the project root:

```env
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
```

**Note:**
- `PORT=443` implies HTTPS. For HTTP (e.g., port `5000`), adjust `PORT` accordingly.
- On first run, the app auto-creates the database and uploads folders.

### Run the Application

```bash
python app.py
```

Access the app at [https://localhost:443](https://localhost:443) (or your configured host/port).

## 🔎 How It Works

### Item Addition Workflow

1. **Login:** Go to `/login` and enter your credentials.
2. **Add Item:** Navigate to `/add` and submit the item's URL.
3. **Capture Images:** Provide 3 clear images:
   - **Blurriness Check:** Ensures image clarity using Laplacian variance.
   - **ORB Descriptors:** Generated and stored for feature matching.
4. **Completion:** After successful uploads, the item is ready for recognition.

### Recognition Workflow

1. **Navigate to `/view`.**
2. **Capture/Upload an Image.**
3. **Processing:**
   - **Blurriness Check:** Ensures image clarity.
   - **ORB Descriptor Computation:** Extract features from the image.
   - **Descriptor Comparison:** Compare against stored items.
4. **Results:**
   - **High Confidence:** Redirect to the item's URL.
   - **Borderline:** Prompt for more images.
   - **No Match:** Notify the user of no match.

## 📁 Project Structure

```
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
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**

    ```bash
    git checkout -b feature/new-stuff
    ```

3. **Commit changes**

    ```bash
    git commit -m 'Add new feature'
    ```

4. **Push to your branch**

    ```bash
    git push origin feature/new-stuff
    ```

5. **Open a Pull Request**

## 📜 License

This project is open-source. Feel free to modify and use it as needed. Check the `LICENSE` file for more details.

## 👤 Author

**Charisn**

Senior Software Engineer passionate about solving problems and exploring new technologies.

Questions or ideas? Open an issue or submit a pull request!

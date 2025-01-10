# REMBG - Background Remover

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0%2B-green)

REMBG is a modern web application that allows users to easily remove backgrounds from images. Built with Flask and featuring a sleek, responsive UI, it provides a seamless experience for processing images with instant results.

## ✨ Features

- 🖼️ One-click background removal
- 👤 User authentication and personal workspaces
- 📱 Responsive design that works on desktop and mobile
- 🎨 Modern UI with smooth animations
- 📂 Image processing history
- ⚡ Real-time processing feedback
- 🔒 Secure file handling
- 💾 Automatic cleanup of user data on logout

## 🛠️ Technology Stack

- **Backend**: Python/Flask
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Image Processing**: rembg
- **Authentication**: Flask-Login
- **UI Components**: Font Awesome, Google Fonts

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rembg.git
cd rembg
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📱 Usage

1. Create an account or login if you already have one
2. Click the upload area or drag and drop an image
3. Wait for automatic background removal
4. Download your processed image
5. Access your processing history anytime

## 🔧 Configuration

The application can be configured through environment variables:

- `SECRET_KEY`: Flask secret key (default: provided in code)
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)
- `PORT`: Server port (default: 5000)

## 📁 Project Structure

```
REMBG/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── instance/          # Database files
├── uploads/           # Temporary upload directory
├── processed/         # Processed images directory
└── templates/         # HTML templates
    ├── index.html    # Main application page
    ├── login.html    # Login page
    └── signup.html   # Registration page
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) for the background removal functionality
- [Tailwind CSS](https://tailwindcss.com/) for the UI framework
- [Flask](https://flask.palletsprojects.com/) for the web framework

## 📧 Contact

Sarthak - [@Sarthakhuh](https://x.com/Sarthakhuh)

Project Link: [https://github.com/yourusername/rembg](https://github.com/Sarthakischill/rembg)

---

If you find this project helpful, please consider giving it a star ⭐️

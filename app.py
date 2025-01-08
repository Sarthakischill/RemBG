from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
import os

# Import from your other modules
from models import db, User, ProcessedImage
from auth import auth, init_login_manager

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Initialize database and login manager
db.init_app(app)
init_login_manager(app)

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the image (Placeholder for actual background removal logic)
        processed_filename = f"processed_{filename}"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        os.rename(file_path, processed_path)  # Example of renaming, replace with actual processing

        # Save image record in the database
        processed_image = ProcessedImage(
            filename=filename,
            original_filename=filename,
            processed_filename=processed_filename,
            user_id=current_user.id
        )
        db.session.add(processed_image)
        db.session.commit()

        flash('Image processed successfully!')
        return redirect(url_for('history'))

    flash('Invalid file format. Only PNG, JPG, and JPEG are allowed.')
    return redirect(url_for('index'))

@app.route('/processed/<filename>')
@login_required
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/history')
@login_required
def history():
    images = ProcessedImage.query.filter_by(user_id=current_user.id).order_by(ProcessedImage.created_at.desc()).all()
    return render_template('history.html', images=images)

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from rembg import remove
from PIL import Image
import os
import uuid
import shutil
from datetime import datetime

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ProcessedImage', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Processed Image Model
class ProcessedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    processed_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Configuration
BASE_UPLOAD_FOLDER = 'uploads'
BASE_PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Create and configure app
app = Flask(__name__)
app.config['SECRET_KEY'] = '07489df73cf90b9f4a93b6dba1a7d1924b7e5d6989d41fa00bef419c8374bee6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BASE_UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER
app.config['BASE_PROCESSED_FOLDER'] = BASE_PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# Ensure base directories exist
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BASE_PROCESSED_FOLDER, exist_ok=True)

def get_user_upload_folder(username):
    folder = os.path.join(app.config['BASE_UPLOAD_FOLDER'], username)
    os.makedirs(folder, exist_ok=True)
    return folder

def get_user_processed_folder(username):
    folder = os.path.join(app.config['BASE_PROCESSED_FOLDER'], username)
    os.makedirs(folder, exist_ok=True)
    return folder

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('index')})
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'success': False, 'error': 'Username already taken'}), 400
    
    user = User(
        email=data.get('email'),
        username=data.get('username')
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    # Create user directories
    get_user_upload_folder(user.username)
    get_user_processed_folder(user.username)
    
    login_user(user)
    return jsonify({'success': True, 'redirect': url_for('index')})

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Delete user's directories
    username = current_user.username
    upload_dir = get_user_upload_folder(username)
    processed_dir = get_user_processed_folder(username)
    
    # Delete the user's images from database
    ProcessedImage.query.filter_by(user_id=current_user.id).delete()
    
    # Remove directories if they exist
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    if os.path.exists(processed_dir):
        shutil.rmtree(processed_dir)
    
    logout_user()
    return jsonify({'success': True})

@app.route('/api/auth/status')
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        })
    return jsonify({'authenticated': False}), 401

@app.route('/api/remove-background', methods=['POST'])
@login_required
def remove_background():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

       # Get user-specific directories
        upload_dir = get_user_upload_folder(current_user.username)
        processed_dir = get_user_processed_folder(current_user.username)

        # Generate unique filename
        unique_filename = f"{str(uuid.uuid4())}_{secure_filename(file.filename)}"
        input_path = os.path.join(upload_dir, unique_filename)
        
        # Save original file
        file.save(input_path)
        
        # Process image
        try:
            input_image = Image.open(input_path)
            output_image = remove(input_image)
            
            processed_filename = f"processed_{unique_filename}"
            output_path = os.path.join(processed_dir, processed_filename)
            
            output_image.save(output_path, 'PNG')
            
            # Save to database
            processed_image = ProcessedImage(
                filename=unique_filename,
                original_filename=file.filename,
                processed_filename=processed_filename,
                user_id=current_user.id
            )
            db.session.add(processed_image)
            db.session.commit()
            
            response = {
                'success': True,
                'message': 'Background removed successfully',
                'processed_image_url': f'/api/images/processed/{processed_filename}',
                'original_image_url': f'/api/images/original/{unique_filename}'
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500
            
        finally:
            # Clean up original file after processing
            if os.path.exists(input_path):
                os.remove(input_path)
                
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
@login_required
def delete_image(image_id):
    try:
        image = ProcessedImage.query.filter_by(id=image_id, user_id=current_user.id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
            
        # Delete the processed file
        processed_path = os.path.join(
            get_user_processed_folder(current_user.username),
            image.processed_filename
        )
        if os.path.exists(processed_path):
            os.remove(processed_path)
            
        # Delete database entry
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error deleting image: {str(e)}'}), 500

@app.route('/api/images/delete/<int:image_id>', methods=['DELETE'])
@login_required
def delete_processed_image(image_id):
    try:
        image = ProcessedImage.query.filter_by(id=image_id, user_id=current_user.id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
            
        # Delete the processed file
        processed_path = os.path.join(
            get_user_processed_folder(current_user.username),
            image.processed_filename
        )
        if os.path.exists(processed_path):
            os.remove(processed_path)
            
        # Delete database entry
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error deleting image: {str(e)}'}), 500

@app.route('/api/images/processed/<filename>')
@login_required
def serve_processed_image(filename):
    # Serve from user's processed directory
    return send_from_directory(
        get_user_processed_folder(current_user.username),
        filename
    )

@app.route('/api/images/original/<filename>')
@login_required
def serve_original_image(filename):
    # Serve from user's upload directory
    return send_from_directory(
        get_user_upload_folder(current_user.username),
        filename
    )

@app.route('/api/images/history')
@login_required
def get_image_history():
    try:
        processed_images = ProcessedImage.query.filter_by(user_id=current_user.id)\
            .order_by(ProcessedImage.created_at.desc()).all()
        
        history = [{
            'id': image.id,
            'filename': image.processed_filename,
            'url': f'/api/images/processed/{image.processed_filename}',
            'date': image.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for image in processed_images]
        
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': f'Error fetching history: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import MediaFile
from utils.image_analyzer import ImageAnalyzer
import os
from datetime import datetime

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ai_bp.route('/analyze-prescription', methods=['POST'])
@jwt_required()
def analyze_prescription():
    """
    Analyze a prescription image using AI
    Expects multipart/form-data with an 'image' file
    """
    current_user_id = int(get_jwt_identity())
    
    # Check if file is present
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only images are allowed'}), 400
    
    try:
        # Create upload folder if it doesn't exist
        upload_folder = '/app/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{current_user_id}_{timestamp}_{file.filename}")
        file_path = os.path.join(upload_folder, filename)
        
        # Save the file
        file.save(file_path)
        
        # Validate image
        analyzer = ImageAnalyzer()
        if not analyzer.validate_image(file_path):
            os.remove(file_path)
            return jsonify({'error': 'Invalid or corrupted image file'}), 400
        
        # Analyze the image with OpenAI
        analysis_result = analyzer.analyze_prescription_image(file_path)
        
        if not analysis_result['success']:
            # Keep the file but return error
            return jsonify({
                'error': analysis_result.get('error', 'Analysis failed'),
                'details': analysis_result.get('details', ''),
                'file_path': f'/uploads/{filename}'
            }), 422
        
        # Save media file record
        media_file = MediaFile(
            user_id=current_user_id,
            original_name=file.filename,
            file_path=f'/uploads/{filename}',
            file_type='image',
            mime_type=file.content_type,
            file_size=os.path.getsize(file_path),
            is_processed=True,
            ai_analysis_result=analysis_result['data']
        )
        
        db.session.add(media_file)
        db.session.commit()
        
        return jsonify({
            'message': 'Image analyzed successfully',
            'analysis': analysis_result['data'],
            'confidence': analysis_result.get('confidence', 'medium'),
            'media_file_id': media_file.id,
            'file_path': f'/uploads/{filename}'
        }), 200
        
    except Exception as e:
        # Clean up file if error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'error': 'Failed to process image',
            'details': str(e)
        }), 500

@ai_bp.route('/extract-text', methods=['POST'])
@jwt_required()
def extract_text():
    """
    Extract text from an image using OCR (simplified version)
    """
    current_user_id = int(get_jwt_identity())
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        upload_folder = '/app/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{current_user_id}_{timestamp}_{file.filename}")
        file_path = os.path.join(upload_folder, filename)
        
        file.save(file_path)
        
        analyzer = ImageAnalyzer()
        base64_image = analyzer.encode_image(file_path)
        
        response = analyzer.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all visible text from this image. Return it as plain text."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        extracted_text = response.choices[0].message.content
        
        return jsonify({
            'text': extracted_text,
            'file_path': f'/uploads/{filename}'
        }), 200
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

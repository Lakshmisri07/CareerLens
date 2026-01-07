"""
Certificate Manager for CareerLens
Handles certificate uploads (images/PDFs) and storage
"""

import os
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
from PIL import Image
import io

class CertificateManager:
    """Manage certificate uploads and storage"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self, upload_folder='static/certificates'):
        self.upload_folder = upload_folder
        # Create folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def get_file_extension(self, filename):
        """Get file extension"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    def generate_unique_filename(self, user_email, original_filename):
        """Generate unique filename for uploaded certificate"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = self.get_file_extension(original_filename)
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        return f"{safe_email}_{timestamp}.{ext}"
    
    def save_certificate(self, file, user_email):
        """
        Save uploaded certificate file
        Returns: dict with file info or None if error
        """
        if not file or file.filename == '':
            return None
        
        if not self.allowed_file(file.filename):
            return {'error': 'Invalid file type. Only PNG, JPG, JPEG, and PDF allowed.'}
        
        try:
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.MAX_FILE_SIZE:
                return {'error': 'File too large. Maximum size is 5MB.'}
            
            # Generate unique filename
            filename = self.generate_unique_filename(user_email, file.filename)
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(filepath)
            
            # Get file info
            file_type = self.get_file_extension(filename)
            
            return {
                'filename': filename,
                'filepath': filepath,
                'url': f'/static/certificates/{filename}',
                'file_type': file_type,
                'file_size': file_size,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Error saving file: {str(e)}'}
    
    def delete_certificate(self, filename):
        """Delete a certificate file"""
        try:
            filepath = os.path.join(self.upload_folder, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting certificate: {e}")
            return False
    
    def get_thumbnail(self, filename, size=(200, 200)):
        """
        Generate thumbnail for image certificates
        Returns base64 encoded thumbnail or None
        """
        try:
            filepath = os.path.join(self.upload_folder, filename)
            ext = self.get_file_extension(filename)
            
            if ext in ['jpg', 'jpeg', 'png']:
                # Open and resize image
                img = Image.open(filepath)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format=ext.upper() if ext != 'jpg' else 'JPEG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/{ext};base64,{img_str}"
            elif ext == 'pdf':
                # Return PDF icon placeholder
                return None
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    def validate_certificate_data(self, cert_data):
        """Validate certificate data before saving to database"""
        required_fields = ['name', 'issuer']
        
        for field in required_fields:
            if not cert_data.get(field):
                return False, f"Missing required field: {field}"
        
        return True, None
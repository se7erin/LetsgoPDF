# app.py - Flask web application for PDF unlocking
from flask import Flask, render_template, request, send_file, session
from werkzeug.utils import secure_filename
import os
import time
import uuid
import PyPDF2
import pikepdf
import threading
import shutil

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
FILE_EXPIRY_MINUTES = 30  # Files will be deleted after this time

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_str(file_path):
    """Get human-readable file size"""
    size_bytes = os.path.getsize(file_path)
    size_kb = size_bytes / 1024
    if size_kb >= 1024:
        size_mb = size_kb / 1024
        return f"{size_mb:.2f} MB"
    else:
        return f"{size_kb:.2f} KB"

def check_pdf_protection(file_path):
    """Check if PDF is password protected"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return pdf_reader.is_encrypted
    except Exception as e:
        print(f"Error checking PDF protection: {e}")
        return "Unknown"

def process_pdf(input_path, output_path):
    """Process the PDF to remove password protection"""
    try:
        # Try pikepdf method first (usually more reliable)
        try:
            with pikepdf.open(input_path, allow_overwriting_input=False) as pdf:
                pdf.save(output_path)
            return True, "PDF successfully unlocked with pikepdf method."
        except Exception as pike_error:
            print(f"pikepdf method failed: {pike_error}")
            # Continue to next method if first method fails
        
        # Try PyPDF2 method as fallback
        try:
            with open(input_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                
                # Try a blank password if the PDF is encrypted
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt('')
                    except:
                        pass
                
                # Create a new PDF writer
                pdf_writer = PyPDF2.PdfWriter()
                
                # Add all pages to the writer
                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Write the result to the output file
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            return True, "PDF successfully unlocked with PyPDF2 method."
        except Exception as pypdf_error:
            print(f"PyPDF2 method failed: {pypdf_error}")
            raise Exception("Could not unlock the PDF with available methods.")
            
    except Exception as e:
        return False, str(e)

def cleanup_old_files():
    """Clean up old uploaded and result files"""
    now = time.time()
    expiry_seconds = FILE_EXPIRY_MINUTES * 60
    
    # Clean uploads folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > expiry_seconds:
            os.remove(file_path)
    
    # Clean results folder
    for filename in os.listdir(app.config['RESULTS_FOLDER']):
        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > expiry_seconds:
            os.remove(file_path)

# Start a background thread to clean up old files periodically
def cleanup_thread():
    while True:
        cleanup_old_files()
        time.sleep(5 * 60)  # Run every 5 minutes

cleanup_thread = threading.Thread(target=cleanup_thread, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                          max_size=MAX_FILE_SIZE_MB, 
                          expiry=FILE_EXPIRY_MINUTES)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return render_template('index.html', 
                              error="No file part", 
                              max_size=MAX_FILE_SIZE_MB, 
                              expiry=FILE_EXPIRY_MINUTES)
    
    file = request.files['file']
    
    if file.filename == '':
        return render_template('index.html', 
                              error="No file selected", 
                              max_size=MAX_FILE_SIZE_MB, 
                              expiry=FILE_EXPIRY_MINUTES)
    
    if not allowed_file(file.filename):
        return render_template('index.html', 
                              error="Only PDF files are allowed", 
                              max_size=MAX_FILE_SIZE_MB, 
                              expiry=FILE_EXPIRY_MINUTES)
    
    try:
        # Generate a unique ID for this file
        file_id = str(uuid.uuid4())
        session['file_id'] = file_id
        
        # Secure the filename and save the uploaded file
        original_filename = secure_filename(file.filename)
        filename = f"{file_id}_{original_filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Save original filename in session
        session['original_filename'] = original_filename
        session['upload_path'] = upload_path
        
        # Get file info
        file_size = get_file_size_str(upload_path)
        is_protected = check_pdf_protection(upload_path)
        
        # Store in session
        session['file_size'] = file_size
        session['is_protected'] = is_protected
        
        return render_template('confirm.html', 
                              filename=original_filename,
                              filesize=file_size,
                              protected="Yes" if is_protected else "No")
    
    except Exception as e:
        return render_template('index.html', 
                              error=f"Error uploading file: {str(e)}", 
                              max_size=MAX_FILE_SIZE_MB, 
                              expiry=FILE_EXPIRY_MINUTES)

@app.route('/process', methods=['POST'])
def process():
    """Process the uploaded PDF"""
    if 'upload_path' not in session or 'original_filename' not in session:
        return render_template('index.html', 
                              error="No uploaded file found. Please upload again.", 
                              max_size=MAX_FILE_SIZE_MB, 
                              expiry=FILE_EXPIRY_MINUTES)
    
    try:
        # Get file information from session
        upload_path = session['upload_path']
        original_filename = session['original_filename']
        
        # Create output filename
        name_without_ext = os.path.splitext(original_filename)[0]
        output_filename = f"{name_without_ext}_unlocked.pdf"
        secure_output_filename = secure_filename(output_filename)
        file_id = session.get('file_id', str(uuid.uuid4()))
        result_filename = f"{file_id}_{secure_output_filename}"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        
        # Process the PDF
        success, message = process_pdf(upload_path, result_path)
        
        if success:
            # Store result path in session for download
            session['result_path'] = result_path
            session['result_filename'] = output_filename
            
            return render_template('success.html', 
                                  filename=original_filename,
                                  output_filename=output_filename,
                                  message=message)
        else:
            return render_template('error.html', 
                                  error=message)
    
    except Exception as e:
        return render_template('error.html', 
                              error=f"Error processing file: {str(e)}")

@app.route('/download')
def download():
    """Download the processed PDF"""
    if 'result_path' not in session or 'result_filename' not in session:
        return render_template('index.html', 
                              error="No processed file found. Please try again.", 
                              max_size=MAX_FILE_SIZE_MB, 
                              expiry=FILE_EXPIRY_MINUTES)
    
    try:
        result_path = session['result_path']
        result_filename = session['result_filename']
        
        return send_file(result_path, 
                        download_name=result_filename, 
                        as_attachment=True)
        
    except Exception as e:
        return render_template('error.html', 
                              error=f"Error downloading file: {str(e)}")

if __name__ == '__main__':
    # For development only - use a proper WSGI server in production
    app.run(debug=True)

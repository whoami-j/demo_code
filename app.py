from flask import Flask, render_template, request, redirect, url_for
import os
import pytesseract
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'receipt_image' not in request.files:
        return redirect(request.url)
    file = request.files['receipt_image']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        # Placeholder for image processing
        output_data = process_image(filename)
        return render_template('index.html', output=output_data)

def process_image(image_path):
    # Open the image file
    image = Image.open(image_path)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding to preprocess the image
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Rescale the image to improve OCR accuracy
    rescaled = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Use pytesseract to do OCR on the preprocessed image
    text = pytesseract.image_to_string(rescaled, lang='eng')
    
    # Post-process the text to replace problematic text within double quotes with dots
    import re
    text = re.sub(r'\"[^\"]*\"', lambda match: '"' + '.' * (len(match.group(0)) - 2) + '"', text)
    
    return text

if __name__ == '__main__':
    app.run(debug=True)

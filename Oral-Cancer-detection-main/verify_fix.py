import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app import MyPDF, generate_pdf
    print("Successfully imported MyPDF and generate_pdf from app.py")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error during import: {e}")
    sys.exit(1)

# Test MyPDF class instantiation
try:
    pdf = MyPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF Generation", ln=True, align='C')
    output_path = "test_output.pdf"
    pdf.output(output_path)
    print(f"Successfully generated test PDF using MyPDF class at {output_path}")
    if os.path.exists(output_path):
        os.remove(output_path)
except Exception as e:
    print(f"Error testing MyPDF class: {e}")
    sys.exit(1)

# Test generate_pdf function (mocking inputs)
# generate_pdf returns a response object (send_file), so we might need to mock flask stuff if it uses it.
# Looking at generate_pdf code:
# It uses os, Image, FPDF. It returns send_file(...)
# send_file requires flask context? 
# Use 'app.test_request_context()'

from flask import Flask
app = Flask(__name__)

with app.test_request_context():
    try:
        # Mock data
        timestamp = "20231027_123456"
        symptoms = {
            "pain_level": "Low",
            "bleeding": "No",
            "swelling": "None", 
            "duration": "1 week",
            "history": "None",
            "habits": ["None"]
        }
        # generate_pdf(prediction, confidence, image_path, timestamp, symptoms)
        # We need a dummy image possibly, or it handles missing images gracefully? 
        # The code checks os.path.exists.
        
        response = generate_pdf("High Risk", 85, "", timestamp, symptoms)
        print("Successfully called generate_pdf")
    except Exception as e:
        print(f"Error testing generate_pdf: {e}")
        #sys.exit(1) # Don't exit yet, check potential causes

# O-SCAN - AI-Powered Oral Cancer Detection System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0%2B-green.svg)

## 📋 Overview

O-SCAN is an advanced web-based medical screening application that uses artificial intelligence to detect oral cancer from uploaded images. The system provides a comprehensive platform for patients and doctors to manage screening records, track symptoms, and facilitate early detection of oral cancer through machine learning analysis.

## 🎯 Key Features

### For Patients
- **AI-Powered Screening**: Upload oral cavity images for instant AI analysis
- **Symptom Tracking**: Record detailed symptoms including pain, bleeding, swelling, and habits
- **Medical History**: Maintain comprehensive health records and lifestyle information
- **Professional Reports**: Generate detailed PDF reports with AI predictions and confidence scores
- **Doctor Consultations**: Book appointments and communicate with healthcare professionals
- **Secure Dashboard**: Personalized patient portal to manage all screening activities

### For Doctors
- **Patient Management**: View and manage patient records and screening history
- **Case Review**: Analyze AI predictions and provide professional medical opinions
- **Appointment System**: Schedule and manage patient consultations
- **Specialized Profiles**: Create professional profiles with medical specializations
- **Communication Hub**: Secure messaging system for patient-doctor interactions

## 🏗️ System Architecture

### Backend Technologies
- **Flask**: Python web framework for application logic
- **SQLAlchemy**: ORM for database management
- **Keras/TensorFlow**: Machine learning model for image analysis
- **Flask-Login**: User authentication and session management
- **FPDF**: PDF report generation

### Frontend Technologies
- **HTML5/CSS3/JavaScript**: Responsive web interface
- **Bootstrap**: Modern UI components and styling
- **Dynamic Templates**: Server-side rendering with Jinja2

### Database Schema
- **Users**: Patient and doctor authentication and profiles
- **Patient Records**: Screening results, symptoms, and medical history
- **Appointments**: Doctor-patient scheduling system
- **AI Predictions**: Machine learning analysis results and confidence scores

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/Yashaswini-ds/oral-cancer.git
cd oral-cancer
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```bash
# Copy the environment file
cp .env.example .env

# Edit .env file with your settings
# Generate a secure secret key:
python -c 'import os; print(os.urandom(24).hex())'
```

### Step 5: Initialize Database
```bash
python create_db.py
```

### Step 6: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📊 AI Model Information

### Model Details
- **Architecture**: Convolutional Neural Network (CNN)
- **Model File**: `oral_cancer_model.h5` (9.9MB)
- **Input**: Oral cavity images (preprocessed to model specifications)
- **Output**: Binary classification (Malignant/Benign) with confidence scores

### Image Processing
- Automatic image normalization and resizing
- Support for common image formats (JPG, PNG)
- Quality enhancement for better analysis accuracy

## 🔧 Configuration

### Environment Variables
```bash
# Security
SECRET_KEY=your_secure_random_string_here

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///oral_cancer.db

# File Upload Settings
UPLOAD_FOLDER=static/uploads/
MAX_CONTENT_LENGTH=16MB
```

### Database Setup
The system uses SQLite by default for development. For production:
```bash
# PostgreSQL (Recommended for production)
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/dbname

# MySQL
SQLALCHEMY_DATABASE_URI=mysql://user:password@localhost/dbname
```

## 📱 Usage Guide

### Patient Workflow
1. **Registration**: Create account with email and password
2. **Profile Setup**: Complete personal and medical information
3. **Screening**: Upload oral cavity images
4. **Symptom Input**: Provide detailed symptoms and medical history
5. **AI Analysis**: Receive instant prediction and confidence score
6. **Report Generation**: Download comprehensive PDF report
7. **Doctor Consultation**: Book appointment if needed

### Doctor Workflow
1. **Registration**: Create professional account with specialization
2. **Dashboard Access**: View assigned patient cases
3. **Case Review**: Analyze AI predictions and patient data
4. **Professional Opinion**: Provide medical assessment
5. **Patient Communication**: Respond to patient queries
6. **Appointment Management**: Schedule and track consultations

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Secure user sessions with Flask-Login
- **File Upload Security**: Filename sanitization and type validation
- **CSRF Protection**: Cross-site request forgery prevention
- **Input Validation**: Comprehensive data validation and sanitization

## 📁 Project Structure

```
oral-cancer/
├── app.py                 # Main Flask application
├── models.py              # Database models and relationships
├── create_db.py           # Database initialization script
├── oral_cancer_model.h5   # Trained AI model
├── static/                # Static assets (CSS, JS, images)
│   ├── uploads/          # User uploaded images
│   └── reports/          # Generated PDF reports
├── templates/            # HTML templates
│   ├── auth.html         # Authentication pages
│   ├── patient_dashboard.html
│   ├── doctor_dashboard.html
│   └── ...
├── instance/             # Database files
├── .env.example          # Environment configuration template
└── README.md             # This file
```

## 🧪 Testing

### Run Application Tests
```bash
python -m pytest tests/
```

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Image upload and AI analysis
- [ ] PDF report generation
- [ ] Doctor-patient communication
- [ ] Appointment scheduling
- [ ] Database operations

## 🚀 Deployment

### Production Deployment with Docker
```bash
# Build Docker image
docker build -t o-scan .

# Run container
docker run -p 5000:5000 o-scan
```

### Environment-Specific Settings
- **Development**: SQLite database, debug mode enabled
- **Production**: PostgreSQL/MySQL, debug disabled, proper logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Medical Disclaimer

**IMPORTANT**: O-SCAN is an AI-assisted screening tool and is NOT a substitute for professional medical diagnosis. The system provides preliminary analysis that should be validated by qualified healthcare professionals. Always consult with medical experts for definitive diagnosis and treatment planning.

## 📞 Support & Contact

- **Repository**: https://github.com/Yashaswini-ds/oral-cancer
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Email**: abhiramgirishnaik@gmail.com

## 🙏 Acknowledgments

- Medical professionals who provided domain expertise
- Open-source community for the amazing tools and libraries
- Patients who contributed to the training dataset
- Healthcare institutions supporting early cancer detection initiatives

---

**Version**: 0.1.3  
**Last Updated**: February 2026  
**Status**: Active Development

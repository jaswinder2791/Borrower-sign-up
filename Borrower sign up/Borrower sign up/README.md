# 🏦 LoanPro - Local Loan Management System

A completely offline loan management system that stores all data locally using SQLite database. No internet connection required!

## ✨ Features

- 📝 **Loan Application Form** - Easy-to-use application form
- 🔍 **Status Tracking** - Check application status anytime
- 👨‍💼 **Admin Panel** - Manage applications and update statuses
- 📊 **Auto Eligibility** - Automatic eligibility calculation
- 💾 **Local Storage** - All data stored in SQLite database
- 🔒 **100% Offline** - No network dependencies

## 🚀 Quick Start

### Method 1: Using the startup script
```bash
chmod +x start_loanpro.sh
./start_loanpro.sh
```

### Method 2: Manual start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 run_local.py
```

### Method 3: Direct Flask run
```bash
python3 app.py
```

## 🌐 Access Points

- **Home Page**: http://localhost:5000
- **Apply for Loan**: http://localhost:5000/apply
- **Check Status**: http://localhost:5000/check-status
- **Admin Panel**: http://localhost:5000/admin
- **View Database**: http://localhost:5000/view-all-applications

## 🔐 Admin Access

- **Username**: admin
- **Password**: admin123

## 💾 Database

- **Type**: SQLite
- **File**: `loanpro.db` (created automatically)
- **Location**: Same directory as application files

## 📊 How It Works

1. **Application Submission**: Users fill the form → Data saved to local database
2. **Eligibility Calculation**: Automatic scoring based on:
   - Age (18-65 optimal)
   - Income level
   - Employment status
   - Loan-to-income ratio
3. **Status Management**: Admin can update application statuses
4. **Local Storage**: Everything stored in SQLite - no network required

## 🛠️ Technical Details

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript
- **Storage**: Local file system
- **Dependencies**: Flask, Flask-SQLAlchemy

## 📁 File Structure

```
loanpro/
├── app.py                 # Main Flask application
├── run_local.py          # Local runner script
├── view_database.py      # Database viewer utility
├── requirements.txt      # Python dependencies
├── start_loanpro.sh     # Startup script
├── loanpro.db           # SQLite database (auto-created)
└── templates/           # HTML templates
    ├── index.html
    ├── apply.html
    ├── status.html
    └── check_status.html
```

## 🔧 Customization

You can easily customize:
- Eligibility scoring criteria in `check_eligibility()` function
- Form fields in `templates/apply.html`
- Admin credentials in `admin_authenticate()` function
- Database schema in the model classes

## 📝 Usage Examples

### Submit Application
1. Go to http://localhost:5000/apply
2. Fill all required fields
3. Submit form
4. Get Application ID for tracking

### Check Status
1. Go to http://localhost:5000/check-status
2. Enter Application ID and Email
3. View detailed status and eligibility

### Admin Management
1. Go to http://localhost:5000/admin
2. Login with admin/admin123
3. View and manage all applications

## 🚫 No Network Required

This system is designed to work completely offline:
- No API calls
- No external databases
- No internet connectivity needed
- All processing happens locally

Perfect for:
- Local testing
- Offline environments
- Privacy-focused applications
- Learning and development

## 📞 Support

This is a local application - all data stays on your computer. Check the console output for any error messages or issues.
```

Now you have a complete, fully functional loan management system that:

1. **Stores data directly in local SQLite database** - no network required
2. **Processes forms immediately** - data goes straight to database
3. **Works completely offline** - no internet dependencies
4. **Includes all necessary templates and functionality**

To run the system:

```bash
python3 run_local.py# LoanPro-

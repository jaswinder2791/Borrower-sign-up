from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import re
from decimal import Decimal
from sqlalchemy import Numeric  # Add this import

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-local-secret-key-12345'
# LOCAL SQLite database - no network required
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loanpro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class LoanApplication(db.Model):
    __tablename__ = 'loan_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    
    # Address Information
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    
    # Financial Information
    employment_status = db.Column(db.String(50), nullable=False)
    annual_income = db.Column(Numeric(12, 2), nullable=False)  # Changed from db.Decimal to Numeric
    loan_amount = db.Column(Numeric(12, 2), nullable=False)    # Changed from db.Decimal to Numeric
    loan_purpose = db.Column(db.String(100), nullable=False)
    
    # Application Status
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    eligibility = db.relationship('EligibilityCheck', backref='application', uselist=False, cascade='all, delete-orphan')
    logs = db.relationship('ApplicationLog', backref='application', cascade='all, delete-orphan')

class EligibilityCheck(db.Model):
    __tablename__ = 'eligibility_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('loan_applications.id'), nullable=False)
    
    # Eligibility Factors
    age_score = db.Column(db.Integer, default=0)
    income_score = db.Column(db.Integer, default=0)
    employment_score = db.Column(db.Integer, default=0)
    loan_to_income_score = db.Column(db.Integer, default=0)
    
    # Overall Results
    total_score = db.Column(db.Integer, default=0)
    percentage = db.Column(Numeric(5, 2), default=0)  # Changed from db.Decimal to Numeric
    status = db.Column(db.String(20), default='pending')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ApplicationLog(db.Model):
    __tablename__ = 'application_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('loan_applications.id'), nullable=False)
    
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Template Filters
@app.template_filter('currency')
def currency_filter(amount):
    """Format amount as Indian Rupees"""
    if amount is None:
        return "₹0"
    return f"₹{amount:,.2f}"

@app.template_filter('date')
def date_filter(date_obj):
    """Format date"""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime('%d %b %Y')

@app.template_filter('datetime')
def datetime_filter(datetime_obj):
    """Format datetime"""
    if datetime_obj is None:
        return ""
    return datetime_obj.strftime('%d %b %Y at %I:%M %p')

@app.template_filter('status_badge')
def status_badge_filter(status):
    """Convert status to HTML badge"""
    status_classes = {
        'pending': 'badge-warning',
        'under_review': 'badge-info',
        'approved': 'badge-success',
        'rejected': 'badge-danger'
    }
    
    status_text = status.replace('_', ' ').title()
    css_class = status_classes.get(status, 'badge-secondary')
    
    return f'<span class="badge {css_class}">{status_text}</span>'

# Utility Functions
def generate_application_id():
    """Generate unique application ID"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = str(uuid.uuid4())[:8].upper()
    return f"LA{timestamp}{random_part}"

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def validate_phone(phone):
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_eligibility(application):
    """Calculate loan eligibility based on various factors"""
    
    # Age Score (18-65 years optimal)
    age = calculate_age(application.date_of_birth)
    if 25 <= age <= 55:
        age_score = 25
    elif 18 <= age <= 65:
        age_score = 20
    else:
        age_score = 10
    
    # Income Score
    annual_income = float(application.annual_income)
    if annual_income >= 1000000:  # 10 Lakhs+
        income_score = 30
    elif annual_income >= 500000:  # 5 Lakhs+
        income_score = 25
    elif annual_income >= 300000:  # 3 Lakhs+
        income_score = 20
    elif annual_income >= 200000:  # 2 Lakhs+
        income_score = 15
    else:
        income_score = 10
    
    # Employment Score
    employment_scores = {
        'employed': 25,
        'self_employed': 20,
        'business_owner': 22,
        'retired': 15,
        'unemployed': 5
    }
    employment_score = employment_scores.get(application.employment_status, 10)
    
    # Loan to Income Ratio Score
    loan_amount = float(application.loan_amount)
    loan_to_income_ratio = loan_amount / annual_income
    
    if loan_to_income_ratio <= 3:
        loan_to_income_score = 20
    elif loan_to_income_ratio <= 5:
        loan_to_income_score = 15
    elif loan_to_income_ratio <= 8:
        loan_to_income_score = 10
    else:
        loan_to_income_score = 5
    
    # Calculate total score and percentage
    total_score = age_score + income_score + employment_score + loan_to_income_score
    percentage = (total_score / 100) * 100
    
    # Determine eligibility status
    if percentage >= 70:
        status = 'highly_eligible'
    elif percentage >= 50:
        status = 'eligible'
    elif percentage >= 30:
        status = 'moderately_eligible'
    else:
        status = 'not_eligible'
    
    return {
        'age_score': age_score,
        'income_score': income_score,
        'employment_score': employment_score,
        'loan_to_income_score': loan_to_income_score,
        'total_score': total_score,
        'percentage': percentage,
        'status': status
    }

def log_application_action(application_id, action, details=None):
    """Log application actions"""
    log = ApplicationLog(
        application_id=application_id,
        action=action,
        details=details
    )
    db.session.add(log)
    db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/submit-application', methods=['POST'])
def submit_application():
    try:
        print("=== FORM SUBMISSION STARTED ===")
        
        # Get form data
        form_data = request.form
        print(f"Form data received: {dict(form_data)}")
        
        # Validate required fields
        required_fields = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'address', 'city', 'state', 'zip_code', 'employment_status',
            'annual_income', 'loan_amount', 'loan_purpose'
        ]
        
        for field in required_fields:
            if not form_data.get(field):
                flash(f'{field.replace("_", " ").title()} is required', 'error')
                return redirect(url_for('apply'))
        
        # Validate email
        if not validate_email(form_data['email']):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('apply'))
        
        # Validate phone
        if not validate_phone(form_data['phone']):
            flash('Please enter a valid 10-digit phone number', 'error')
            return redirect(url_for('apply'))
        
        # Parse date of birth
        try:
            dob = datetime.strptime(form_data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            flash('Please enter a valid date of birth', 'error')
            return redirect(url_for('apply'))
        
        # Validate age
        age = calculate_age(dob)
        if age < 18:
            flash('You must be at least 18 years old to apply', 'error')
            return redirect(url_for('apply'))
        if age > 80:
            flash('Maximum age limit is 80 years', 'error')
            return redirect(url_for('apply'))
        
        # Validate loan amount
        try:
            loan_amount = Decimal(form_data['loan_amount'])
            if loan_amount < 10000:
                flash('Minimum loan amount is ₹10,000', 'error')
                return redirect(url_for('apply'))
            if loan_amount > 10000000:  # 1 Crore
                flash('Maximum loan amount is ₹1,00,00,000', 'error')
                return redirect(url_for('apply'))
        except (ValueError, TypeError):
            flash('Please enter a valid loan amount', 'error')
            return redirect(url_for('apply'))
        
        # Validate annual income
        try:
            annual_income = Decimal(form_data['annual_income'])
            if annual_income < 100000:  # 1 Lakh minimum
                flash('Minimum annual income required is ₹1,00,000', 'error')
                return redirect(url_for('apply'))
        except (ValueError, TypeError):
            flash('Please enter a valid annual income', 'error')
            return redirect(url_for('apply'))
        
        print("=== VALIDATION PASSED ===")
        
        # Create application
        application = LoanApplication(
            application_id=generate_application_id(),
            first_name=form_data['first_name'].strip(),
            last_name=form_data['last_name'].strip(),
            email=form_data['email'].strip().lower(),
            phone=form_data['phone'].strip(),
            date_of_birth=dob,
            address=form_data['address'].strip(),
            city=form_data['city'].strip(),
            state=form_data['state'],
            zip_code=form_data['zip_code'].strip(),
            employment_status=form_data['employment_status'],
            annual_income=annual_income,
            loan_amount=loan_amount,
            loan_purpose=form_data['loan_purpose']
        )
        
        print(f"=== SAVING APPLICATION TO DATABASE ===")
        print(f"Application ID: {application.application_id}")
        print(f"Name: {application.first_name} {application.last_name}")
        print(f"Email: {application.email}")
        print(f"Loan Amount: ₹{application.loan_amount}")
        
        db.session.add(application)
        db.session.flush()  # Get the ID without committing
        
        print(f"Application saved with ID: {application.id}")
        
        # Calculate eligibility
        eligibility_data = check_eligibility(application)
        print(f"Eligibility calculated: {eligibility_data['percentage']:.1f}%")
        
        eligibility = EligibilityCheck(
            application_id=application.id,
            age_score=eligibility_data['age_score'],
            income_score=eligibility_data['income_score'],
            employment_score=eligibility_data['employment_score'],
            loan_to_income_score=eligibility_data['loan_to_income_score'],
            total_score=eligibility_data['total_score'],
            percentage=Decimal(str(eligibility_data['percentage'])),
            status=eligibility_data['status']
        )
        
        db.session.add(eligibility)
        db.session.commit()
        
        print("=== DATABASE COMMIT SUCCESSFUL ===")
        
        # Log the application submission
        log_application_action(application.id, 'application_submitted', 'New loan application submitted')
        log_application_action(application.id, 'eligibility_checked', f'Eligibility calculated: {eligibility_data["percentage"]:.1f}%')
        
        print("=== APPLICATION LOGS CREATED ===")
        
        flash(f'Application submitted successfully! Your Application ID is: {application.application_id}', 'success')
        return redirect(url_for('application_status', app_id=application.application_id))
        
    except Exception as e:
        db.session.rollback()
        print(f"=== ERROR OCCURRED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while submitting your application. Please try again.', 'error')
        return redirect(url_for('apply'))

@app.route('/status/<app_id>')
def application_status(app_id):
    application = LoanApplication.query.filter_by(application_id=app_id).first()
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('status.html', application=application)

@app.route('/check-status', methods=['GET', 'POST'])
def check_status():
    if request.method == 'POST':
        application_id = request.form.get('application_id', '').strip()
        
        if not application_id:
            flash('Please enter an Application ID', 'error')
            return render_template('check_status.html')
        
        # Find the application
        application = LoanApplication.query.filter_by(application_id=application_id).first()
        
        if not application:
            flash('Application not found. Please check your Application ID and try again.', 'error')
            return render_template('check_status.html')
        
        # Redirect to status page with the application
        return render_template('status.html', application=application)
    
    return render_template('check_status.html')

@app.route('/search-application', methods=['POST'])
def search_application():
    app_id = request.form.get('application_id', '').strip()
    email = request.form.get('email', '').strip().lower()
    
    if not app_id or not email:
        flash('Please provide both Application ID and Email', 'error')
        return redirect(url_for('check_status'))
    
    application = LoanApplication.query.filter_by(
        application_id=app_id,
        email=email
    ).first()
    
    if not application:
        flash('Application not found. Please check your Application ID and Email.', 'error')
        return redirect(url_for('check_status'))
    
    return redirect(url_for('application_status', app_id=app_id))

# Admin Routes
@app.route('/admin')
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/authenticate', methods=['POST'])
def admin_authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple authentication (in production, use proper password hashing)
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        flash('Login successful', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get statistics
    total_apps = LoanApplication.query.count()
    pending_apps = LoanApplication.query.filter_by(status='pending').count()
    approved_apps = LoanApplication.query.filter_by(status='approved').count()
    rejected_apps = LoanApplication.query.filter_by(status='rejected').count()
    
    stats = {
        'total': total_apps,
        'pending': pending_apps,
        'approved': approved_apps,
        'rejected': rejected_apps
    }
    
    # Get recent applications (last 10)
    recent_applications = LoanApplication.query.order_by(LoanApplication.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', stats=stats, applications=recent_applications)

@app.route('/admin/applications')
def admin_applications():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    # Build query
    query = LoanApplication.query
    
    if status_filter:
        query = query.filter(LoanApplication.status == status_filter)
    
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            db.or_(
                LoanApplication.first_name.ilike(search_pattern),
                LoanApplication.last_name.ilike(search_pattern),
                LoanApplication.email.ilike(search_pattern),
                LoanApplication.application_id.ilike(search_pattern)
            )
        )
    
    # Get applications ordered by creation date (newest first)
    applications = query.order_by(LoanApplication.created_at.desc()).all()
    
    return render_template('admin_applications.html', applications=applications)

@app.route('/admin/application/<app_id>', methods=['GET', 'POST'])
def admin_application_detail(app_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    application = LoanApplication.query.filter_by(application_id=app_id).first()
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('admin_applications'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action in ['approve', 'reject', 'under_review', 'pending']:
            # Quick action buttons
            application.status = action
            application.updated_at = datetime.utcnow()
            
            try:
                db.session.commit()
                flash(f'Application status updated to {action.replace("_", " ").title()}', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error updating application status', 'error')
                
        elif action == 'update_status':
            # Status update form
            new_status = request.form.get('status')
            notes = request.form.get('notes', '')
            
            if new_status in ['pending', 'under_review', 'approved', 'rejected']:
                application.status = new_status
                application.updated_at = datetime.utcnow()
                
                # You could add notes to a separate table if needed
                # For now, we'll just update the status
                
                try:
                    db.session.commit()
                    flash(f'Application status updated to {new_status.replace("_", " ").title()}', 'success')
                    if notes:
                        flash(f'Notes added: {notes}', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error updating application status', 'error')
        
        return redirect(url_for('admin_application_detail', app_id=app_id))
    
    return render_template('admin_application_detail.html', application=application)

@app.route('/admin/update-status/<app_id>', methods=['POST'])
def admin_update_status(app_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        comment = data.get('comment', '')
        
        if new_status not in ['pending', 'under_review', 'approved', 'rejected']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        application = LoanApplication.query.filter_by(application_id=app_id).first()
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        old_status = application.status
        application.status = new_status
        application.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the status change
        log_details = f'Status changed from {old_status} to {new_status}'
        if comment:
            log_details += f'. Comment: {comment}'
        
        log_application_action(application.id, 'status_updated', log_details)
        
        return jsonify({'success': True, 'message': 'Status updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# View all applications route (for easy database viewing)
@app.route('/view-all-applications')
def view_all_applications():
    """Simple route to view all applications in database"""
    applications = LoanApplication.query.order_by(LoanApplication.created_at.desc()).all()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Applications - LoanPro</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .status-pending { color: orange; }
            .status-approved { color: green; }
            .status-rejected { color: red; }
            .status-under_review { color: blue; }
        </style>
    </head>
    <body>
        <h1>All Loan Applications</h1>
        <p>Total Applications: """ + str(len(applications)) + """</p>
        <table>
            <tr>
                <th>Application ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Loan Amount</th>
                <th>Annual Income</th>
                <th>Status</th>
                <th>Eligibility %</th>
                <th>Created At</th>
            </tr>
    """
    
    for app in applications:
        eligibility_pct = app.eligibility.percentage if app.eligibility else 0
        html += f"""
            <tr>
                <td>{app.application_id}</td>
                <td>{app.first_name} {app.last_name}</td>
                <td>{app.email}</td>
                <td>{app.phone}</td>
                <td>₹{app.loan_amount:,.2f}</td>
                <td>₹{app.annual_income:,.2f}</td>
                <td class="status-{app.status}">{app.status.replace('_', ' ').title()}</td>
                <td>{eligibility_pct:.1f}%</td>
                <td>{app.created_at.strftime('%d %b %Y %I:%M %p')}</td>
            </tr>
        """
    
    html += """
        </table>
        <br>
        <a href="/">← Back to Home</a> | 
        <a href="/admin">Admin Panel</a>
    </body>
    </html>
    """
    
    return html

# API Routes
@app.route('/api/application/<app_id>')
def api_get_application(app_id):
    application = LoanApplication.query.filter_by(application_id=app_id).first()
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    return jsonify({
        'application_id': application.application_id,
        'status': application.status,
        'applicant_name': f"{application.first_name} {application.last_name}",
        'loan_amount': float(application.loan_amount),
        'created_at': application.created_at.isoformat(),
        'eligibility': {
            'percentage': float(application.eligibility.percentage) if application.eligibility else 0,
            'status': application.eligibility.status if application.eligibility else 'pending'
        }
    })

@app.route('/api/stats')
def api_get_stats():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Monthly application stats
    monthly_stats = db.session.query(
        db.func.strftime('%Y-%m', LoanApplication.created_at).label('month'),
        db.func.count(LoanApplication.id).label('count')
    ).group_by('month').order_by('month').all()
    
    # Status distribution
    status_stats = db.session.query(
        LoanApplication.status,
        db.func.count(LoanApplication.id).label('count')
    ).group_by(LoanApplication.status).all()
    
    return jsonify({
        'monthly_applications': [{'month': stat.month, 'count': stat.count} for stat in monthly_stats],
        'status_distribution': [{'status': stat.status, 'count': stat.count} for stat in status_stats]
    })

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# Context Processors
@app.context_processor
def inject_app_name():
    return dict(app_name='LoanPro')

@app.context_processor
def inject_current_year():
    return dict(current_year=datetime.now().year)

# Initialize Database
def init_db():
    """Initialize database with tables"""
    with app.app_context():
        # Create database file if it doesn't exist
        db.create_all()
        print("✅ Database tables created successfully!")
        print(f"📁 Database file: {os.path.abspath('loanpro.db')}")
        
        # Check if database is working
        try:
            test_count = LoanApplication.query.count()
            print(f"📊 Current applications in database: {test_count}")
        except Exception as e:
            print(f"❌ Database error: {e}")

if __name__ == '__main__':
    print("🚀 Starting LoanPro Application...")
    print("📍 Running in LOCAL MODE - No network required")
    print("💾 Data will be stored in local SQLite database")
    
    # Initialize database
    init_db()
    
    print("\n🌐 Application URLs:")
    print("   Main App: http://localhost:5000")
    print("   Apply for Loan: http://localhost:5000/apply")
    print("   Check Status: http://localhost:5000/check-status")
    print("   Admin Panel: http://localhost:5000/admin")
    print("   View All Data: http://localhost:5000/view-all-applications")
    print("\n🔐 Admin Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n⚡ Press Ctrl+C to stop the server")
    
    # Run the application
    app.run(
        debug=True,
        host='127.0.0.1',  # Only localhost - no network access
        port=5000,
        use_reloader=True
    )
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from config import Config
from models import db, User, Job, Swipe

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize Flask-Mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your_email@gmail.com',      # Replace with your email
    MAIL_PASSWORD='your_app_password'          # Replace with app password
)
mail = Mail(app)

# -------------------------
# Home / Redirect
# -------------------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard') if current_user.role == 'user' else url_for('company_dashboard'))
    return redirect(url_for('login'))

# -------------------------
# Register Route
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password, role=role)

        # Common fields
        user.phone = request.form.get('phone', '')
        user.location = request.form.get('location', '')
        

        # User-specific
        if role == 'user':
            user.skills = request.form.get('skills', '')
            user.experience_level = request.form.get('experience_level', '')
            user.education = request.form.get('education', '')

            # Resume upload
            if 'resume' in request.files:
                resume_file = request.files['resume']
                if resume_file.filename:
                    filename = f"{user.email}_{resume_file.filename}"
                    resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user.resume = filename

        # Company-specific
        elif role == 'company':
            user.company_size = request.form.get('company_size', '')
            user.website = request.form.get('website', '')
            user.industry = request.form.get('industry', '')
            user.description = request.form.get('description', '')

        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')
# -------------------------
# Profile Edit Route
# -------------------------
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.location = request.form.get('location')

        if current_user.role == 'user':
            current_user.skills = request.form.get('skills')
            current_user.experience_level = request.form.get('experience_level')
            current_user.education = request.form.get('education')

        elif current_user.role == 'company':
            current_user.company_size = request.form.get('company_size')
            current_user.website = request.form.get('website')
            current_user.industry = request.form.get('industry')
            current_user.description = request.form.get('description')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile_edit.html')

# -------------------------
# Login Route
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard') if current_user.role == 'user' else url_for('company_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard') if user.role == 'user' else url_for('company_dashboard'))
        flash('Invalid email or password.', 'error')

    return render_template('login.html')

# -------------------------
# Logout Route
# -------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------------------------
# User Dashboard (Swipe)
# -------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'user':
        return redirect(url_for('company_dashboard'))
    return render_template('dashboard.html')

# -------------------------
# Liked Jobs Page
# -------------------------
@app.route('/liked_jobs')
@login_required
def liked_jobs():
    if current_user.role != 'user':
        return redirect(url_for('dashboard'))
    swipes = Swipe.query.filter_by(user_id=current_user.id, liked=True).all()
    liked_jobs_list = [Job.query.get(s.job_id) for s in swipes]
    return render_template('liked_jobs.html', jobs=liked_jobs_list)

# -------------------------
# Upload Resume
# -------------------------
@app.route('/upload_resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if current_user.role != 'user':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if 'resume' in request.files:
            resume_file = request.files['resume']
            if resume_file.filename:
                filename = f"{current_user.email}_{resume_file.filename}"
                resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.resume = filename
                db.session.commit()
                flash('Resume uploaded successfully!', 'success')
                return redirect(url_for('dashboard'))
    return render_template('upload_resume.html')

# -------------------------
# API: Get Jobs
# -------------------------
@app.route('/api/jobs')
@login_required
def get_jobs():
    if current_user.role != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    swiped_ids = [s.job_id for s in Swipe.query.filter_by(user_id=current_user.id).all()]
    query = Job.query
    if swiped_ids:
        query = query.filter(~Job.id.in_(swiped_ids))
    jobs = query.all()

    user_skills = [s.strip().lower() for s in (current_user.skills or "").split(',')]
    def score_job(job):
        job_skills = [s.strip().lower() for s in (job.skills or "").split(',')]
        return len(set(user_skills).intersection(set(job_skills)))
    jobs.sort(key=score_job, reverse=True)

    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company_name': job.company_name,
        'description': job.description,
        'skills': job.skills
    } for job in jobs]

    return jsonify({'jobs': jobs_data})

# -------------------------
# Swipe Action
# -------------------------
@app.route('/swipe/<int:job_id>/<action>', methods=['POST'])
@login_required
def swipe(job_id, action):
    if current_user.role != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    liked = (action == 'like')
    if Swipe.query.filter_by(user_id=current_user.id, job_id=job_id).first():
        return jsonify({'status': 'already_swiped'})

    swipe_entry = Swipe(user_id=current_user.id, job_id=job_id, liked=liked)
    db.session.add(swipe_entry)
    db.session.commit()

    # Send resume to company via email
    if liked:
        job = Job.query.get(job_id)
        company = User.query.get(job.company_id)
        if company.email and current_user.resume:
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume)
            msg = Message(
                subject=f"New Applicant for {job.title}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[company.email],
                body=f"User {current_user.name} ({current_user.email}) applied for {job.title}."
            )
            try:
                with app.open_resource(resume_path) as fp:
                    msg.attach(current_user.resume, "application/pdf", fp.read())
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email: {e}")

    return jsonify({'status': 'success'})

# -------------------------
# Job Detail
# -------------------------
@app.route('/job/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

# -------------------------
# Company Dashboard
# -------------------------
@app.route('/company/dashboard')
@login_required
def company_dashboard():
    if current_user.role != 'company':
        return redirect(url_for('dashboard'))

    jobs = Job.query.filter_by(company_id=current_user.id).all()
    for job in jobs:
        job.likes_count = Swipe.query.filter_by(job_id=job.id, liked=True).count()
        job.applicants = Swipe.query.filter_by(job_id=job.id, liked=True).all()
    return render_template('company_dashboard.html', jobs=jobs)

# -------------------------
# Company Add Job
# -------------------------
@app.route('/company/add-job', methods=['GET', 'POST'])
@login_required
def add_job():
    if current_user.role != 'company':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        job = Job(
            title=request.form.get('title'),
            company_name=current_user.name,
            company_id=current_user.id,
            description=request.form.get('description'),
            skills=request.form.get('skills')
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('add_job.html')

# -------------------------
# Run App
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
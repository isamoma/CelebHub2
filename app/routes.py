import os
import re
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from .models import Celebrity, User, CelebritySubmission, OnboardingRegistration, USE_MONGO
from . import DB, login_manager, ME
from flask_login import login_user, login_required, logout_user, current_user
from flask import abort
from werkzeug.utils import secure_filename
from .forms import LoginForm, CelebrityForm ,DeleteCelebrityForm,FeaturedForm,ContactForm,CelebritySubmissionForm,OnboardingForm
from flask_mail import Message
from app import mail

ALLOWED_EXT = {'png','jpg','jpeg','gif'}

# Database abstraction helpers for dual-mode support
def save_object(obj):
    """Save object to database (works for both MongoEngine and SQLAlchemy)"""
    if USE_MONGO:
        obj.save()
    else:
        DB.session.add(obj)
        DB.session.commit()

def delete_object(obj):
    """Delete object from database (works for both MongoEngine and SQLAlchemy)"""
    if USE_MONGO:
        obj.delete()
    else:
        DB.session.delete(obj)
        DB.session.commit()

# Query helper methods
def get_user_by_id(user_id):
    """Get user by ID (works for both database modes)"""
    if USE_MONGO:
        return User.objects(pk=int(user_id)).first()
    else:
        return User.query.get(int(user_id))

def get_user_by_username(username):
    """Get user by username (works for both database modes)"""
    if USE_MONGO:
        return User.objects(username=username).first()
    else:
        return User.query.filter_by(username=username).first()

def get_celebrity_by_id(celeb_id):
    """Get celebrity by ID (works for both database modes)"""
    if USE_MONGO:
        return Celebrity.objects(id=celeb_id).first()
    else:
        return Celebrity.query.get(celeb_id)

def get_celebrity_by_slug(slug):
    """Get celebrity by slug (works for both database modes)"""
    if USE_MONGO:
        return Celebrity.objects(slug=slug).first()
    else:
        return Celebrity.query.filter_by(slug=slug).first()

def get_celebrity_submissions_pending():
    """Get all pending celebrity submissions (works for both database modes)"""
    if USE_MONGO:
        return CelebritySubmission.objects(status="pending").order_by('-created_at')
    else:
        return CelebritySubmission.query.filter_by(status="pending").order_by(CelebritySubmission.created_at.desc()).all()

def get_submission_by_id(submission_id):
    """Get submission by ID (works for both database modes)"""
    if USE_MONGO:
        return CelebritySubmission.objects(id=submission_id).first()
    else:
        return CelebritySubmission.query.get(submission_id)

def get_featured_celebrities():
    """Get all featured celebrities (works for both database modes)"""
    if USE_MONGO:
        return Celebrity.objects(featured=True)
    else:
        return Celebrity.query.filter_by(featured=True).all()

def get_onboarding_registrations_all():
    """Get all onboarding registrations (works for both database modes)"""
    if USE_MONGO:
        return OnboardingRegistration.objects.order_by('-created_at')
    else:
        return OnboardingRegistration.query.order_by(OnboardingRegistration.created_at.desc()).all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT


def generate_unique_slug(name):
    # Basic slugify
    base = re.sub(r'[^a-z0-9]+', '-', (name or '').lower()).strip('-') or 'celeb'
    candidate = base
    idx = 1
    # Query existing slugs that start with base
    if USE_MONGO:
        existing = {s.slug for s in Celebrity.objects(slug__startswith=base).only('slug')}
    else:
        existing = {s.slug for s in Celebrity.query.filter(Celebrity.slug.like(f'{base}%')).all()}
    while candidate in existing:
        idx += 1
        candidate = f"{base}-{idx}"
    return candidate

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)

@login_manager.user_loader
def load_user(user_id):
    try:
        return get_user_by_id(user_id)
    except Exception:
        return None

@main_bp.route('/')
def index():
    q = request.args.get('q', '').strip()

    # Base query: only featured celebrities
    celebs_qs = get_featured_celebrities()

    # If a search query exists, filter by name (but still featured only)
    if q:
        if USE_MONGO:
            celebs_qs = [c for c in celebs_qs if q.lower() in c.name.lower()]
        else:
            celebs_qs = [c for c in celebs_qs if q.lower() in c.name.lower()]

    # Order featured ones by newest first
    if USE_MONGO:
        celebs = sorted(celebs_qs, key=lambda x: x.created_at, reverse=True)
    else:
        celebs = sorted(celebs_qs, key=lambda x: x.created_at, reverse=True)

    return render_template('index.html', celebs=celebs, q=q)

@main_bp.route('/celebrity/<slug>')
def profile(slug):
    celeb = get_celebrity_by_slug(slug)
    if not celeb:
        abort(404)
    return render_template('profile.html', celeb=celeb)

@main_bp.route('/featured')
def featured():
    return render_template('featured.html')
@main_bp.route('/about')
def about():
    return render_template('about.html')
import requests
from flask import current_app
@main_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")

@main_bp.route("/terms")
def terms():
    return render_template("terms.html")


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        api_key = os.getenv("BREVO_API_KEY")
        to_email = os.getenv("MAIL_TO")

        payload = {
            "sender": {"name": form.name.data, "email": form.email.data},
            "to": [{"email": to_email}],
            "subject": f"New message from {form.name.data}",
            "htmlContent": f"""
                <h2>New Contact Message</h2>
                <p><strong>Name:</strong> {form.name.data}</p>
                <p><strong>Email:</strong> {form.email.data}</p>
                <p><strong>Message:</strong><br>{form.message.data}</p>
            """
        }

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            r = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                json=payload,
                headers=headers
            )

            print("BREVO RESPONSE:", r.json())

            if r.status_code == 201:
                flash("Your message was sent successfully!", "success")
            else:
                flash("Failed to send email. Check logs.", "danger")

        except Exception as e:
            print("EMAIL ERROR:", e)
            flash("Error sending email.", "danger")

        return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)

@main_bp.route('/faqs')
def faqs():
    faq_data ={
        "1. What is CelebHub?": "CelebHub is a central platform showcasing verified Kenyan celebrities, influencers, artists, content creators, and public figures. Our goal is to make it easy for fans, brands, and event planners to discover, connect, and engage with Kenyan talent.",
        "2. How can I contact a celebrity featured on CelebHub?": "Each celebrity profile includes links to their official social media pages, YouTube channel,TikTok account, and Spotify listings. We do not share private contact details unless publicly available.",
        "3. Can I feature my celebrity profile on CelebHub?":"Yes. Public figures, artists, creators, and influencers can request a featured profile upgrade by submitting a payment through our official page. Once payment is confirmed, your profile will appear at the top of the homepage.",
        "4. Is there a fee to get featured?":"Yes. Celebrities pay a small one-time fee of Ksh 500 to appear under the “Featured Celebrities” section. This helps with verification, design, and platform maintenance.",
        "5. How long does a featured listing last?":"Featured listings last 30 days. You may renew your listing at any time by repeating the payment process.",
        "6. Is CelebHub official or government certified?":"No. CelebHub is an independent platform built to promote Kenyan talent and simplify access to their public profiles. We do not impersonate or claim official representation.",
        "7. How does CelebHub verify celebrity accounts?":"Our verification team manually checks the social media pages and activity of each celebrity before approving their profile on our platform.",
        "8. Can fans create profiles on CelebHub?":"No. Only celebrities, artists, creators, and influencers are allowed to have profiles. Fan accounts are not supported.",
        "9. How do I request a correction or update to my profile?":"If you are a celebrity with an existing profile, you can reach us via the Contact Page and our admin team will review and update your information.",
        "10. How can brands collaborate with celebrities through CelebHub?":"Brands looking for partnerships, ads, or influencer collaborations can use our Contact Page to reach us. We will assist in connecting you to the appropriate celebrity when possible."
    }

    return render_template('faqs.html', faqs=faq_data)

@main_bp.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    form = OnboardingForm()

    if form.validate_on_submit():
        # Save to DB
        record = OnboardingRegistration(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        save_object(record)

        # Admin notification (Brevo)
        api_key = os.getenv("BREVO_API_KEY")
        admin_email = os.getenv("MAIL_TO")

        payload = {
            "sender": {"name": "CelebHub Notifications", "email": "no-reply@celebhub.co.ke"},
            "to": [{"email": admin_email}],
            "subject": "New User Onboarding Registration",
            "htmlContent": f"""
                <h2>New Onboarding Registration</h2>
                <p><strong>Name:</strong> {form.name.data}</p>
                <p><strong>Email:</strong> {form.email.data}</p>
                <p><strong>Phone:</strong> {form.phone.data}</p>
                <p><strong>Message:</strong> {form.message.data}</p>
                <p>Submitted on: {record.created_at}</p>
            """
        }

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }

        try:
            requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        except Exception:
            pass  # Disable errors from breaking the page

        flash("Thank you! You have successfully joined our onboarding list.", "success")
        return redirect(url_for("main.onboarding"))

    return render_template('onboarding.html', form=form)


@main_bp.route('/submit-celebrity', methods=['GET', 'POST'])
def submit_celeb():
    form = CelebritySubmissionForm()

    if form.validate_on_submit():

        # 📌 Save uploaded photo
        photo = form.photo.data
        filename = None
        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # 📌 Save to database
        submission = CelebritySubmission(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            category=form.category.data,
            bio=form.bio.data,
            youtube=form.youtube.data,
            tiktok=form.tiktok.data,
            spotify=form.spotify.data,
            photo_filename=filename
        )
        save_object(submission)

        # 📩 Send admin notification (Brevo)
        api_key = os.getenv("BREVO_API_KEY")
        admin_email = os.getenv("MAIL_TO")

        payload = {
            "sender": {"name": "CelebHub Submission", "email": "no-reply@celebhub.co.ke"},
            "to": [{"email": admin_email}],
            "subject": "New Celebrity Submission",
            "htmlContent": f"""
                <h2>New Celebrity Submission</h2>
                <p><strong>Name:</strong> {form.name.data}</p>
                <p><strong>Email:</strong> {form.email.data}</p>
                <p><strong>Phone:</strong> {form.phone.data}</p>
                <p><strong>Category:</strong> {form.category.data}</p>
                <p><strong>Bio:</strong> {form.bio.data}</p>
                <p>Status: <strong>Pending Review</strong></p>
            """
        }

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }

        requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)

        flash("Your profile has been submitted! Admin will review it shortly.", "success")
        return redirect(url_for('main.submit_celeb'))

    return render_template('submit_celeb.html', form=form)


    
# Admin routes
@admin_bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = get_user_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html', form=form)
@admin_bp.route('/create_admin')
def create_admin():
    from .models import User
    u = User(username="admin")
    u.set_password("admin123")
    save_object(u)
    return "Admin created!"

@admin_bp.route('/celebrities')
@login_required
def celebrities():
    if USE_MONGO:
        celebs = Celebrity.objects.order_by('-created_at')
    else:
        celebs = Celebrity.query.order_by(Celebrity.created_at.desc()).all()
    return render_template('admin/celebrities.html', celebs=celebs ,form=FeaturedForm)
@admin_bp.route('/submissions')
@login_required
def submissions():
    pending_submissions = get_celebrity_submissions_pending()
    return render_template('admin/submissions.html', submissions=pending_submissions)
@admin_bp.route('/submissions/<int:id>')
@login_required
def view_submission(id):
    sub = get_submission_by_id(id)
    if not sub:
        abort(404)
    return render_template('admin/view_submission.html', sub=sub)
@admin_bp.route('/submission/<int:id>/approve', methods=['POST'])
@login_required
def approve_submission(id):
    sub = get_submission_by_id(id)
    if not sub:
        abort(404)

    # Create a new Celebrity from submitted data
    # Generate a unique, safe slug for the new celebrity
    slug = generate_unique_slug(sub.name or f'celeb-{sub.id}')

    new_celeb = Celebrity(
        name=sub.name,
        slug=slug,
        category=sub.category,
        bio=sub.bio,
        photo_filename=sub.photo_filename,
        youtube=sub.youtube,
        tiktok=sub.tiktok,
        spotify=sub.spotify,
    )
    save_object(new_celeb)

    # Update submission status
    sub.status = "approved"
    save_object(sub)

    flash("Submission approved and added to Celebrities!", "success")
    return redirect(url_for('admin.submissions'))

    
@admin_bp.route('/submission/<int:id>/reject', methods=['POST'])
@login_required
def reject_submission(id):
    sub = get_submission_by_id(id)
    if not sub:
        abort(404)
    sub.status = "rejected"
    save_object(sub)
    flash("Submission rejected.", "danger")
    return redirect(url_for('admin.submissions'))
@admin_bp.route('/onboarding-users')
@login_required
def onboarding_users():
    users = get_onboarding_registrations_all()
    return render_template('admin/onboarding_users.html', users=users)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def dashboard():
    if USE_MONGO:
        celebs = Celebrity.objects.order_by('-created_at')
    else:
        celebs = Celebrity.query.order_by(Celebrity.created_at.desc()).all()
    form= DeleteCelebrityForm()
    return render_template('admin/dashboard.html', form=form, celebs=celebs)

@admin_bp.route('/add', methods=['GET','POST'])
@login_required
def add_celeb():
    form = CelebrityForm()
    if form.validate_on_submit():
        photo_file = request.files.get('photo')
        featured=request.form.get('Featured')=='true'
        filename = None
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(save_path)
        new = Celebrity(name=form.name.data, slug=form.slug.data, bio=form.bio.data,
                category=form.category.data, photo_filename=filename,
                youtube=form.youtube.data, tiktok=form.tiktok.data, spotify=form.spotify.data,
                featured=form.featured.data)
        save_object(new)
        flash('Celebrity added', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_profile.html', form=form)

@admin_bp.route('/edit/<int:cid>', methods=['GET', 'POST'])
@login_required
def edit_celeb(cid):
    celeb = get_celebrity_by_id(cid)
    if not celeb:
        abort(404)
    form = CelebrityForm()
    # Populate form data for editing
    if request.method == 'GET':
        form.name.data = celeb.name
        form.slug.data = celeb.slug
        form.category.data = celeb.category
        form.bio.data = celeb.bio
        form.youtube.data = celeb.youtube
        form.tiktok.data = celeb.tiktok
        form.spotify.data = celeb.spotify
        form.featured.data = celeb.featured

    if form.validate_on_submit():
        # Handle photo upload
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(save_path)

            # Remove old photo if different
            if celeb.photo_filename and celeb.photo_filename != filename:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], celeb.photo_filename))
                except Exception:
                    pass

            celeb.photo_filename = filename

        # Update text fields
        celeb.name = form.name.data
        celeb.slug = form.slug.data
        celeb.bio = form.bio.data
        celeb.category = form.category.data
        celeb.youtube = form.youtube.data
        celeb.tiktok = form.tiktok.data
        celeb.spotify = form.spotify.data
        
        # ✅ Correctly handle 'featured' checkbox
        celeb.featured = form.featured.data  

        save_object(celeb)
        flash('Celebrity updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_profile.html', form=form, celeb=celeb)


@admin_bp.route('/delete/<int:cid>', methods=['POST'])
@login_required
def delete_celebrity(cid):
    form = DeleteCelebrityForm()
    if form.validate_on_submit():
        celeb = get_celebrity_by_id(cid)
        if not celeb:
            flash('Celebrity not found', 'danger')
            return redirect(url_for('admin.dashboard'))
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], celeb.photo_filename))
        except Exception:
            pass
        delete_object(celeb)
        flash(f'{celeb.name} has been deleted successfully', 'success')
    else:
        flash('Invalid delete request','danger')
    return redirect(url_for('admin.dashboard'))


import requests, base64
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, instance_relative_config=True)

@app.route('/pay', methods=['POST'])
def mpesa_payment():
    phone = request.json.get('phone')
    amount = request.json.get('amount', 1)
    
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    shortcode = os.getenv('MPESA_SHORTCODE')
    passkey = os.getenv('MPESA_PASSKEY')
    callback_url = os.getenv('MPESA_CALLBACK_URL')
    
    # Generate access token
    token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(token_url, auth=(consumer_key, consumer_secret))
    access_token = r.json().get('access_token')
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode('utf-8')
    
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": "CelebHub",
        "TransactionDesc": "Featured Listing Payment"
    }

    res = requests.post("https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    return jsonify(res.json())
@app.route('/mpesa/token')
def generate_token():
    import requests, os
    from requests.auth import HTTPBasicAuth

    key = os.getenv("MPESA_CONSUMER_KEY")
    secret = os.getenv("MPESA_CONSUMER_SECRET")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(key, secret))

    return response.json()

import os
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from .models import Celebrity, User
from . import DB, login_manager
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .forms import LoginForm, CelebrityForm ,DeleteCelebrityForm,FeaturedForm,ContactForm
from flask_mail import Message
from app import mail

ALLOWED_EXT = {'png','jpg','jpeg','gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main_bp.route('/')
def index():
    q = request.args.get('q', '').strip()

    # Base query: only featured celebrities
    query = Celebrity.query.filter_by(featured=True)

    # If a search query exists, filter by name (but still featured only)
    if q:
        query = query.filter(Celebrity.name.ilike(f"%{q}%"))

    # Order featured ones by newest first
    celebs = query.order_by(Celebrity.created_at.desc()).all()

    return render_template('index.html', celebs=celebs, q=q)


@main_bp.route('/celebrity/<slug>')
def profile(slug):
    celeb = Celebrity.query.filter_by(slug=slug).first_or_404()
    return render_template('profile.html', celeb=celeb)

@main_bp.route('/featured')
def featured():
    return render_template('featured.html')
@main_bp.route('/about')
def about():
    return render_template('about.html')
import requests
from flask import current_app

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

    
# Admin routes
@admin_bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html', form=form)
@admin_bp.route('/celebrities')
@login_required
def celebrities():
    celebs = Celebrity.query.order_by(Celebrity.created_at.desc()).all()
    return render_template('admin/celebrities.html', celebs=celebs ,form=FeaturedForm)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def dashboard():
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
        DB.session.add(new)
        DB.session.commit()
        flash('Celebrity added', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_profile.html', form=form)

@admin_bp.route('/edit/<int:cid>', methods=['GET', 'POST'])
@login_required
def edit_celeb(cid):
    celeb = Celebrity.query.get_or_404(cid)
    form = CelebrityForm(obj=celeb)

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

        DB.session.commit()
        flash('Celebrity updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_profile.html', form=form, celeb=celeb)


@admin_bp.route('/delete/<int:cid>', methods=['POST'])
@login_required
def delete_celebrity(cid):
    form = DeleteCelebrityForm()
    if form.validate_on_submit():
        celeb = Celebrity.query.get_or_404(cid)
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], celeb.photo_filename))
        except Exception:
            pass
        DB.session.delete(celeb)
        DB.session.commit()
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

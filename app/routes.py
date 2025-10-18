import os
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from .models import Celebrity, User
from . import DB, login_manager
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .forms import LoginForm, CelebrityForm

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
    q = request.args.get('q', '')
    if q:
        celebs = Celebrity.query.filter(Celebrity.name.ilike(f"%{q}%")).order_by(Celebrity.created_at.desc()).all()
    else:
        celebs = Celebrity.query.order_by(Celebrity.is_featured.desc(), Celebrity.created_at.desc()).all()
    return render_template('index.html', celebs=celebs, q=q)

@main_bp.route('/celebrity/<slug>')
def profile(slug):
    celeb = Celebrity.query.filter_by(slug=slug).first_or_404()
    return render_template('profile.html', celeb=celeb)
@main_bp.route('/')
def home():
    # Show only featured celebs on homepage
    featured_celebs = Celebrity.query.filter_by(is_featured=True).all()
    return render_template('index.html', celebs=featured_celebs)

@main_bp.route('/celebrities')
def celebrities():
    # Show all celebs
    all_celebs = Celebrity.query.all()
    return render_template('celebrities.html', celebs=all_celebs)

@main_bp.route('/featured')
def featured():
    return render_template('featured.html')


import requests, base64
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()


@main_bp.route('/pay', methods=['POST'])
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

    res = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    return jsonify(res.json())

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

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def dashboard():
    celebs = Celebrity.query.order_by(Celebrity.created_at.desc()).all()
    return render_template('admin/dashboard.html', celebs=celebs)

@admin_bp.route('/add', methods=['GET','POST'])
@login_required
def add_celeb():
    form = CelebrityForm()
    if form.validate_on_submit():
        photo_file = request.files.get('photo')
        filename = None
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(save_path)
        new = Celebrity(name=form.name.data, slug=form.slug.data, bio=form.bio.data,
                        category=form.category.data, photo_filename=filename,
                        youtube=form.youtube.data, tiktok=form.tiktok.data, spotify=form.spotify.data,
                        is_featured=form.is_featured.data)
        DB.session.add(new)
        DB.session.commit()
        flash('Celebrity added', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_profile.html', form=form)

@admin_bp.route('/edit/<int:cid>', methods=['GET','POST'])
@login_required
def edit_celeb(cid):
    celeb = Celebrity.query.get_or_404(cid)
    form = CelebrityForm(obj=celeb)
    if form.validate_on_submit():
        # handle photo replacement
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(save_path)
            # remove old file if different
            if celeb.photo_filename and celeb.photo_filename != filename:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], celeb.photo_filename))
                except Exception:
                    pass
            celeb.photo_filename = filename
        celeb.name = form.name.data
        celeb.slug = form.slug.data
        celeb.bio = form.bio.data
        celeb.category = form.category.data
        celeb.youtube = form.youtube.data
        celeb.tiktok = form.tiktok.data
        celeb.spotify = form.spotify.data
        celeb.is_featured = form.is_featured.data
        DB.session.commit()
        flash('Updated', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_profile.html', form=form, celeb=celeb)

@admin_bp.route('/delete/<int:cid>', methods=['POST'])
@login_required
def delete_celeb(cid):
    celeb = Celebrity.query.get_or_404(cid)
    # remove file if exists
    if celeb.photo_filename:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], celeb.photo_filename))
        except Exception:
            pass
    DB.session.delete(celeb)
    DB.session.commit()
    flash('Deleted', 'success')
    return redirect(url_for('admin.dashboard'))
@admin_bp.route('/toggle_feature/<int:celeb_id>', methods=['POST'])
@login_required
def toggle_feature(celeb_id):
    celeb = Celebrity.query.get_or_404(celeb_id)
    celeb.is_featured = not celeb.is_featured
    DB.session.commit()
    return redirect(url_for('admin.dashboard'))

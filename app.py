import os
import pandas as pd
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename



app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


gifts_df = pd.read_csv('gifts_data.csv')
gifts_df['image'] = gifts_df['image'].fillna('default.jpg').astype(str)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    bio = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    dark_mode = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(300))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'static', 'main']
    if request.endpoint not in allowed_routes and not current_user.is_authenticated:
        return redirect(url_for('login'))

@app.route('/')
def main():
    return render_template('main2.html')

@app.route('/index')
def home():
    categories = gifts_df['category'].unique()
    return render_template('index.html', categories=categories, gifts=gifts_df.to_dict(orient='records'))

@app.route('/filter', methods=['GET'])
def filter_gifts():
    category = request.args.get('category', default=None)
    filtered_gifts = gifts_df[gifts_df['category'] == category] if category else gifts_df
    categories = gifts_df['category'].unique()
    return render_template('index.html', gifts=filtered_gifts.to_dict(orient='records'), categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first():
        flash('Email уже зарегистрирован!', 'danger')
        return redirect(url_for('login'))

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash('Аккаунт создан! Теперь войдите в систему.', 'success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.bio = request.form.get('bio')

        date_str = request.form.get('date_of_birth')
        if date_str:
            current_user.date_of_birth = datetime.strptime(date_str, '%Y-%m-%d').date()

        current_user.gender = request.form.get('gender')
        current_user.dark_mode = 'dark_mode' in request.form

        avatar = request.files.get('avatar')
        if avatar and avatar.filename:
            filename = secure_filename(avatar.filename)
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            avatar.save(avatar_path)
            current_user.avatar_url = url_for('static', filename=f'uploads/{filename}')

        db.session.commit()
        flash('Профиль обновлён!', 'success')
        return redirect(url_for('profile'))

    return render_template('profil.html', user=current_user)

@app.route('/admin_hub')
@login_required
def admin_hub():
    return render_template('Nub.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

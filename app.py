import os
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
if 'id' not in gifts_df.columns:
    gifts_df.insert(0, 'id', range(1, len(gifts_df) + 1))
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
    recipients = gifts_df['recipient'].unique()
    holidays = gifts_df['holiday'].unique()
    return render_template('index.html', categories=categories, recipients=recipients, holidays=holidays, gifts=gifts_df.to_dict(orient='records'))

@app.route('/filter', methods=['GET'])
def filter_gifts():
    category = request.args.get('category')
    recipient = request.args.get('recipient')
    holiday = request.args.get('holiday')
    filtered_gifts = gifts_df
    if category:
        filtered_gifts = filtered_gifts[filtered_gifts['category'] == category]
    if recipient:
        filtered_gifts = filtered_gifts[filtered_gifts['recipient'] == recipient]
    if holiday:
        filtered_gifts = filtered_gifts[filtered_gifts['holiday'] == holiday]
    categories = gifts_df['category'].unique()
    recipients = gifts_df['recipient'].unique()
    holidays = gifts_df['holiday'].unique()
    return render_template('index.html', gifts=filtered_gifts.to_dict(orient='records'), categories=categories, recipients=recipients, holidays=holidays)

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    all_gifts = gifts_df.to_dict(orient='records')
    filtered_gifts = [gift for gift in all_gifts if query in gift['name'].lower() or query in gift['description'].lower()]
    categories = gifts_df['category'].unique()
    recipients = gifts_df['recipient'].unique()
    holidays = gifts_df['holiday'].unique()
    return render_template('index.html', gifts=filtered_gifts, categories=categories, recipients=recipients, holidays=holidays)

@app.route('/wishlist')
def wishlist():
    wishlist_ids = session.get('wishlist', [])
    wishlist_gifts = gifts_df[gifts_df['id'].isin(wishlist_ids)]
    return render_template('wishlist.html', gifts=wishlist_gifts.to_dict(orient='records'))

@app.route('/add_to_wishlist/<int:gift_id>', methods=['POST'])
def add_to_wishlist(gift_id):
    wishlist = session.get('wishlist', [])
    if gift_id not in wishlist:
        wishlist.append(gift_id)
        session['wishlist'] = wishlist
        session.modified = True
    return redirect(url_for('gift_detail', gift_id=gift_id))

@app.route('/remove_from_wishlist/<int:gift_id>', methods=['POST'])
def remove_from_wishlist(gift_id):
    wishlist = session.get('wishlist', [])
    if gift_id in wishlist:
        wishlist.remove(gift_id)
    session['wishlist'] = wishlist
    return redirect(url_for('wishlist'))

@app.route('/gift/<int:gift_id>')
@login_required
def gift_detail(gift_id):
    gift = gifts_df[gifts_df['id'] == gift_id].to_dict(orient='records')
    if not gift:
        flash('Подарок не найден.', 'danger')
        return redirect(url_for('home'))
    return render_template('gift_detail.html', gift=gift[0])

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
    gifts = gifts_df.to_dict(orient='records')
    return render_template('profil.html', user=current_user, gifts=gifts)

@app.route('/admin_hub', methods=['GET', 'POST'])
@login_required
def admin_hub():
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
        return redirect(url_for('admin_hub'))
    gifts = gifts_df.to_dict(orient='records')
    return render_template('Nub.html', user=current_user, gifts=gifts)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('login'))


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_gift = db.Column(db.Boolean, default=False)
    gift_id = db.Column(db.Integer, nullable=True)

@app.route('/messenger')
@login_required
def messenger():
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | 
        (Conversation.user2_id == current_user.id)
    ).all()
    return render_template('messenger.html', conversations=conversations, gifts=gifts_df.to_dict('records'))

@app.route('/api/messages/<int:conversation_id>')
@login_required
def get_messages(conversation_id):
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.sent_at).all()
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'content': msg.content,
        'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M'),
        'is_gift': msg.is_gift,
        'gift_id': msg.gift_id
    } for msg in messages])

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    new_message = Message(
        conversation_id=data['conversation_id'],
        sender_id=current_user.id,
        content=data['content'],
        is_gift=data.get('is_gift', False),
        gift_id=data.get('gift_id')
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/search_users')
@login_required
def search_users():
    query = request.args.get('query', '')
    users = User.query.filter(User.username.ilike(f'%{query}%')).filter(User.id != current_user.id).all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'avatar_url': user.avatar_url
    } for user in users])

@app.route('/api/start_conversation/<int:user_id>', methods=['POST'])
@login_required
def start_conversation(user_id):
    conv = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
        ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    if not conv:
        conv = Conversation(user1_id=current_user.id, user2_id=user_id)
        db.session.add(conv)
        db.session.commit()
    
    return jsonify({'conversation_id': conv.id})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




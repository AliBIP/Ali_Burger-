import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
  
app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

gifts_df = pd.read_csv('gifts_data.csv')
gifts_df['image'] = gifts_df['image'].fillna('default.jpg')  
gifts_df['image'] = gifts_df['image'].astype(str)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def main():
    return render_template('main.html')

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

@app.route('/admin_hub')
@login_required
def admin_hub():
    return render_template('Nub.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Успешный вход!', 'success')
            return redirect(url_for('admin_hub'))
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

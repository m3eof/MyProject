from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                if username == 'admin':
                    if password == '1234':
                        login_user(user)
                        return redirect(url_for('admin'))
                else:
                    login_user(user)
                    return redirect(url_for('profile'))
        
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/admin')
def admin():
    if current_user.is_authenticated:
        return render_template('admin.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully')
            return redirect(url_for('login'))
    return render_template('Reg.html')

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user = current_user
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))
    
    return render_template('editprofile.html', user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/web')
def web():
    return render_template('web.html')

@app.route('/webinfo')
def webinfo():
    return render_template('webinfo.html')

@app.route('/webnews')
def webnews():
    return render_template('webnews.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080)

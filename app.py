from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ffb6af3ff6506d966950d33874104411'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    donations = db.relationship('Donation', backref='user', lazy=True)


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


@app.before_request
def create_tables():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


# User registration page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:
            return "Username already exists"

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    else:
        return render_template('signup.html')


# User login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = username

            if user.donations:
                return redirect('/dashboard')
            else:
                return redirect('/donate')
        else:
            return redirect('/login')
    else:
        return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# Donation form submission
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        currency = request.form['currency']
        user = User.query.filter_by(username=session['user']).first()

        donation = Donation(name=name, amount=amount, currency=currency, user=user)
        db.session.add(donation)
        db.session.commit()

        return redirect('/thankyou')

    return render_template('donate.html')


# Thank you page
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


# Admin login page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'adminpassword':
            session['admin'] = True
            return redirect('/admin/donations')
        else:
            return redirect('/admin/login')
    else:
        return render_template('admin_login.html')


# Admin dashboard to view donations
@app.route('/admin/donations')
def admin_donations():
    if 'admin' in session:
        donations = Donation.query.all()
        return render_template('admin_dashboard.html', donations=donations)
    else:
        return redirect('/admin/login')


# Admin approve donation
@app.route('/admin/approve/<int:donation_id>', methods=['POST'])
def admin_approve_donation(donation_id):
    if 'admin' in session:
        donation = Donation.query.get(donation_id)
        if donation:
            donation.approved = True
            db.session.commit()
    return redirect('/admin/donations')


# User dashboard to view donations and status
@app.route('/dashboard')
def user_dashboard():
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        donations = user.donations
        return render_template('dashboard.html', donations=donations)
    else:
        return redirect('/login')


# Total amount raised in different currencies
@app.route('/total_amount')
def total_amount():
    currencies = db.session.query(Donation.currency).distinct().all()
    total_amounts = []
    for currency in currencies:
        total_amount = db.session.query(db.func.sum(Donation.amount)).filter_by(currency=currency[0], approved=True).scalar()
        total_amounts.append((currency[0], total_amount))
    return render_template('total_amount.html', total_amounts=total_amounts)


if __name__ == '__main__':
    app.run(debug=True)

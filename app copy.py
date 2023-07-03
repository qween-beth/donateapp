from flask import Flask, render_template, session, request, redirect

app = Flask(__name__)

# Define a list to store donation data
donations = []

# Set a secret key for session management
app.secret_key = '5748ba62456c71838415eac7a887237d'

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Donation form submission
@app.route('/donate', methods=['POST'])
def donate():
    # Retrieve form data
    name = request.form['name']
    amount = float(request.form['amount'])

    # Add donation data to the list
    donations.append({'name': name, 'amount': amount, 'approved': False})

    return redirect('/thankyou')

# Admin dashboard to approve donations
@app.route('/admin')
def admin():
    # Check if the user is logged in
    if 'admin' in session:
        return render_template('admin.html', donations=donations)
    else:
        return redirect('/login')

# Donation approval
@app.route('/approve/<int:index>')
def approve(index):
    # Check if the user is logged in
    if 'admin' in session:
        # Update the 'approved' flag of the donation
        donations[index]['approved'] = True
        return redirect('/admin')
    else:
        return redirect('/login')

# Login page
@app.route('/login')
def login():
    return render_template('login.html')

# Login submission
@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']

    # Check if the provided credentials are correct
    if username == 'admin' and password == 'password':
        session['admin'] = True
        return redirect('/admin')
    else:
        return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

# Thank you page
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

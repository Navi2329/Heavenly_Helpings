import random
from flask import Flask, jsonify, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__, static_folder='static')
app.secret_key = 'h#3gR52m$Pq56wJ@v^*8x4p$^Sb5&vK9'

app.config['MYSQL_USER'] = 'azureuser'
app.config['MYSQL_PASSWORD'] = 'helpings@123'
app.config['MYSQL_HOST'] = 'dbms-project.mysql.database.azure.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'db'
mysql = MySQL(app)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/donation')
def donation():
    return render_template('donation.html')


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'email' in session:
        email = session['email']
        query = "SELECT u_name FROM user WHERE u_email = %s"
        query1 = "SELECT u_email FROM user WHERE u_email = %s"
        query2 = "SELECT dob FROM user WHERE u_email = %s"
        query3 = "SELECT u_pno FROM user WHERE u_email = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (email,))
        result = cur.fetchone()
        name = result[0] if result else 'GUEST'
        cur.execute(query1, (email,))
        result1 = cur.fetchone()
        email = result1[0] if result1 else 'GUEST'
        cur.execute(query2, (email,))
        result2 = cur.fetchone()
        dob = result2[0] if result2 else 'GUEST'
        cur.execute(query3, (email,))
        result3 = cur.fetchone()
        phone = result3[0] if result3 else 'GUEST'
        return render_template('profile.html', name=name, email=email,dob=dob,phone=phone)
    else:
        return render_template('profile.html', name='GUEST')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM user WHERE u_email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    if user and password == user[4]:
        session['email'] = email
        return redirect('/home')
    else:
        error = 'Invalid email or password. Please try again.'
        return render_template('login.html', error=error)


@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    cur = mysql.connection.cursor()
    user_id = random.randint(1011, 999999)
    cur.execute('SELECT * FROM user WHERE u_email = %s', (email,))
    user = cur.fetchone()
    if user:
        error = 'Email already exists. Please log in or use a different email.'
        return render_template('login.html', error=error)
    cur.execute('INSERT INTO user (u_id,u_name, u_email, u_pass) VALUES (%s, %s, %s, %s)',
                (user_id, name, email, password))
    mysql.connection.commit()
    cur.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()

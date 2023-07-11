import random
import datetime
from flask import Flask, jsonify, render_template, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'h#3gR52m$Pq56wJ@v^*8x4p$^Sb5&vK9'

app.config['MYSQL_USER'] = 'azureuser'
app.config['MYSQL_PASSWORD'] = 'helpings@123'
app.config['MYSQL_HOST'] = 'dbms-project.mysql.database.azure.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'db'
mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


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
        query = "SELECT u_name, u_email, dob, u_pno, location, u_profile_photo,roles FROM user WHERE u_email = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (email,))
        result = cur.fetchone()
        if result:
            name, email, dob, phone, loc, profile_photo, roles = result
        else:
            name, email, dob, phone, loc, profile_photo, roles = 'GUEST', 'GUEST', 'GUEST', 'GUEST', 'GUEST', None
        cur.close()
        return render_template(
            'profile.html',
            name=name,
            email=email,
            dob=dob,
            phone=phone,
            loc=loc,
            profile_photo=profile_photo,
            roles=roles
        )
    else:
        return render_template(
            'profile.html',
            name='GUEST',
            email='GUEST',
            dob='GUEST',
            phone='GUEST',
            loc='GUEST',
            profile_photo=None,
            roles='GUEST'
        )


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'email' in session:
        email = session['email']
        data = request.get_json()
        location = data.get('location')
        dob = data.get('dob')
        phone = data.get('phone')
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE user SET location = %s, dob = %s, u_pno = %s WHERE u_email = %s",
            (location, dob_date, phone, email)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Profile updated successfully'})
    else:
        return jsonify({'error': 'Guest user cannot update profile'})


@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    if 'email' in session:
        email = session['email']
        file = request.files.get('profile_picture')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            relative_path = "uploads/" + filename
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE user SET u_profile_photo = %s WHERE u_email = %s",
                (relative_path, email)
            )
            mysql.connection.commit()
            cur.close()
            return jsonify({'success': True, 'profile_photo': relative_path})
        else:
            return jsonify({'success': False, 'message': 'Invalid file format or no file selected'})
    else:
        return jsonify({'success': False, 'error': 'Guest user cannot update profile'})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
    cur.execute(
        'INSERT INTO user (u_id,u_name, u_email, u_pass) VALUES (%s, %s, %s, %s)',
        (user_id, name, email, password)
    )
    mysql.connection.commit()
    cur.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.route('/search_temples', methods=['POST'])
def search_temples():
    if 'email' in session:
        temple_name = request.form.get('temple_name')
        cur = mysql.connection.cursor()
        cur.execute("SELECT t_name, t_add, history FROM temple WHERE t_name LIKE %s", (f"%{temple_name}%",))
        temples = cur.fetchall()
        cur.close()
        return render_template('temple.html', temples=temples)
    else:
        return redirect('/')

@app.route('/temples', methods=['GET', 'POST'])
def temples():
    if request.method == 'POST':
        search_input = request.form.get('search_input')
        if search_input:
            cur = mysql.connection.cursor()
            cur.execute("SELECT t_name, t_add, history FROM temple WHERE t_name LIKE %s", (f'%{search_input}%',))
            filtered_temples = cur.fetchall()
            cur.close()
            return render_template('temple.html', temples=temples, filtered_temples=filtered_temples)
    cur = mysql.connection.cursor()
    cur.execute("SELECT t_name, t_add, history FROM temple")
    temples = cur.fetchall()
    cur.close()
    return render_template('temple.html', temples=temples)



@app.route('/search_centers', methods=['POST'])
def search_centers():
    if 'email' in session:
        temple_name = request.form.get('temple_name')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM subsidised_food WHERE s_name LIKE %s", (f"%{temple_name}%",))
        temples = cur.fetchall()
        cur.close()
        return render_template('subsidised.html', subsidized_centers=temples)
    else:
        return redirect('/')

@app.route('/subsidised', methods=['GET', 'POST'])
def subsidised():
    if request.method == 'POST':
        search_input = request.form.get('search_input')
        if search_input:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM subsidised_food WHERE s_name LIKE %s", (f'%{search_input}%',))
            filtered_temples = cur.fetchall()
            cur.close()
            return render_template('subsidised.html', temples=temples, filtered_temples=filtered_temples)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subsidised_food")
    temples = cur.fetchall()
    cur.close()
    return render_template('subsidised.html', subsidized_centers=temples)




if __name__ == '__main__':
    app.run(debug=True)

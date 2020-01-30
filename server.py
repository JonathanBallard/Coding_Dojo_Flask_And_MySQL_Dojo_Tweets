from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL    # import the function that will return an instance of a connection
import re

from flask_bcrypt import Bcrypt        

app = Flask(__name__)
app.secret_key = "secretstuff"
bcrypt = Bcrypt(app)     # we are creating an object called bcrypt, 
                         # which is made by invoking the function Bcrypt with our app as an argument

@app.route('/')
def index():
    mysql = connectToMySQL("email_registration")
    users = mysql.query_db("SELECT * FROM users;")
    print(users)
    return render_template("index.html", all_users = users)


@app.route('/register', methods=['POST'])
def register():
    mysql = connectToMySQL("email_registration")
    users = mysql.query_db("SELECT * FROM users;")
    print(users)
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
    PW_REGEX = re.compile(r'^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$')
    firstName = request.form['first_name']
    lastName = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    conPassword = request.form['passwordConfirm']
    form = request.form['formType']
    isValid = True
    pwHash = bcrypt.generate_password_hash(password).decode('utf-8')


    if len(firstName) <= 0:
        isValid = False
        flash('Please enter a first name', 'name')

    if not firstName.isalpha():
        isValid = False
        flash('Please enter a first name using only alphabetic characters', 'name')

    if len(lastName) <= 0:
        isValid = False
        flash('Please enter a last name', 'name')

    if not lastName.isalpha():
        isValid = False
        flash('Please enter a last name using only alphabetic characters', 'name')

    if len(email) <= 3:
        isValid = False
        flash('Please enter an email address', 'email')

    if not EMAIL_REGEX.match(request.form['email']):
        isValid = False
        flash("Invalid email address!", 'email')

    if not PW_REGEX.match(request.form['password']):
        isValid = False
        flash("Invalid password! Minimum 8 characters, 1 number, and 1 special character", 'password')

    if len(password) <= 4:
        isValid = False
        flash('Please enter a valid password (minimum 5 characters)', 'password')

    if not password == conPassword:
        isValid = False
        flash('Password doesnt match confirm password', 'password')

    
    
    if isValid == True:
        mysql = connectToMySQL("email_registration")
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(fname)s, %(lname)s, %(email)s, %(pw)s);"
        data = {
            "fname": firstName,
            "lname": lastName,
            "email": email,
            "pw": pwHash
        }
        new_user_id = mysql.query_db(query, data)

        mysql = connectToMySQL("email_registration")
        users = mysql.query_db("SELECT * FROM users;")
        print(users)
        flash('Success!')
        return redirect('/')
    else:
        return redirect('/')

@app.route('/destroy', methods=['POST'])
def destroy():
    session.clear()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("email_registration")
    emailDB = mysql.query_db("SELECT email FROM users;")
    print(emailDB)
    form = request.form['formType']

    email = request.form['emailLogin']
    password = str(request.form['passwordLogin'])
    data = {
        "em": email
    }

    mysql = connectToMySQL("email_registration")
    query = "SELECT password FROM users WHERE email= %(em)s;"
    login_id = mysql.query_db(query, data)
    
    
    # userId
    mysql = connectToMySQL("email_registration")
    query = "SELECT first_name FROM users WHERE email = %(em)s;"
    userId = mysql.query_db(query, data)
    
    # print('login_id ***********************************', login_id[0]['password'])
    # if not str(email) in emailDB:
    if not [emailCheck for emailCheck in emailDB if emailCheck['email'] == email]:
        print('EmailCheck ****************************', email)
        flash('Email not in our database', 'email')
        return redirect('/')
    else:
        hashCheck = bcrypt.check_password_hash(login_id[0]['password'], password)
        print('hashCheck ***************************************', hashCheck)
        if not hashCheck:
            flash('Invalid Password', password)
            return redirect('/')
        else:
            flash("Successfully Logged In!")
            if not 'user_id' in session:
                session['user_id'] = userId[0]['first_name']
                print('Session[user_id] *******---------------+***********', session['user_id'])
            return redirect('/dashboard')


@app.route('/dashboard', methods=['POST'])
def dashboard():

    
    return render_template('welcome.html')
if __name__ == "__main__":
    app.run(debug=True)
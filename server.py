# TODO
# check session['id']
# DUPLICATES on EDIT




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
    mysql = connectToMySQL("dojo_tweets")
    users = mysql.query_db("SELECT * FROM users;")
    print(users)
    return render_template("index.html", all_users = users)


@app.route('/register', methods=['POST'])
def register():
    mysql = connectToMySQL("dojo_tweets")
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
        flash('Please enter a first name', 'register')

    if not firstName.isalpha():
        isValid = False
        flash('Please enter a first name using only alphabetic characters', 'register')

    if len(lastName) <= 0:
        isValid = False
        flash('Please enter a last name', 'register')

    if not lastName.isalpha():
        isValid = False
        flash('Please enter a last name using only alphabetic characters', 'register')

    if len(email) <= 3:
        isValid = False
        flash('Please enter an email address', 'register')

    if not EMAIL_REGEX.match(request.form['email']):
        isValid = False
        flash("Invalid email address!", 'register')

    if not PW_REGEX.match(request.form['password']):
        isValid = False
        flash("Invalid password! Minimum 8 characters, 1 number, and 1 special character", 'register')

    if len(password) <= 4:
        isValid = False
        flash('Please enter a valid password (minimum 5 characters)', 'register')

    if not password == conPassword:
        isValid = False
        flash('Password doesnt match confirm password', 'register')

    
    
    if isValid == True:
        mysql = connectToMySQL("dojo_tweets")
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(fname)s, %(lname)s, %(email)s, %(pw)s);"
        data = {
            "fname": firstName,
            "lname": lastName,
            "email": email,
            "pw": pwHash
        }
        new_user_id = mysql.query_db(query, data)

        mysql = connectToMySQL("dojo_tweets")
        users = mysql.query_db("SELECT * FROM users;")
        print(users)
        flash('Success!')
        return redirect('/')
    else:
        return redirect('/')

@app.route('/destroy', methods=['POST','GET'])
def destroy():
    session.clear()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("dojo_tweets")
    emailDB = mysql.query_db("SELECT email FROM users;")
    print(emailDB)
    form = request.form['formType']

    email = request.form['emailLogin']
    password = str(request.form['passwordLogin'])
    data = {
        "em": email
    }

    # check emails for request.form['email']
    mysql = connectToMySQL("dojo_tweets")
    query = "SELECT email FROM users WHERE email = %(em)s;"
    emailCheckDB = mysql.query_db(query, data)

    # check if emailCheckDB is populated
    if len(emailCheckDB) == 0:
        emailCheckDBFull = False
    else:
        emailCheckDBFull = True

    mysql = connectToMySQL("dojo_tweets")
    query = "SELECT password FROM users WHERE email= %(em)s;"
    login_id = mysql.query_db(query, data)
    
    
    # userId
    mysql = connectToMySQL("dojo_tweets")
    query = "SELECT first_name FROM users WHERE email = %(em)s;"
    userId = mysql.query_db(query, data)


    # userId
    mysql = connectToMySQL("dojo_tweets")
    query = "SELECT id FROM users WHERE email = %(em)s;"
    idDict = mysql.query_db(query, data)

    if len(idDict) > 0:
        session['id'] = idDict[0]['id']
        
    # print('login_id ***********************************', login_id[0]['password'])
    # if not str(email) in emailDB:
    if not emailCheckDBFull:
        print('EmailCheck ****************************', 'email')
        flash('Email not in our database', 'login')
        return redirect('/')
    else:
        hashCheck = bcrypt.check_password_hash(login_id[0]['password'], password)
        print('hashCheck ***************************************', hashCheck)
        if not hashCheck:
            flash('Invalid Password', 'login')
            return redirect('/')
        else:
            flash("Successfully Logged In!")
            if not 'user_id' in session:
                session['user_id'] = userId[0]['first_name']
                print('Session[user_id] *******---------------+***********', session['user_id'])
            return redirect('/dashboard')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if not session['id']:
        return redirect('/')

    mysql = connectToMySQL("dojo_tweets")
    userFriends = mysql.query_db(f"SELECT followed_user_id FROM follows WHERE follower_user_id = {session['id']} OR user_id = {session['id']}")


    # return list of tweets for welcome.html
    mysql = connectToMySQL("dojo_tweets")
    # tweetList = mysql.query_db(f"SELECT * FROM tweets")   #SELECT ALL TWEETS
    # tweetList = mysql.query_db(f"SELECT * FROM tweets WHERE user_id = {session['id']}")  #ONLY SHOW TWEETS THAT PERSON MADE


    friendsList = list()

    for index in range(len(userFriends)):
        print('INDEX+++++++++++++++++++++++++++++++++', index)
        # friendsList[index].append(userFriends[index]['followed_user_id'])
        x = userFriends[index]['followed_user_id']

    # friendsList = [4,6]

    # tweetList = mysql.query_db(f"SELECT * FROM tweets WHERE user_id IN {friendsList}")  #SELECT MY AND FRIENDS TWEETS
    # print('TWEETLIST =======__________________________________=====', tweetList)


    
    tweetList = mysql.query_db(f"SELECT * FROM tweets JOIN users ON tweets.user_id = users.id JOIN follows ON users.id = follows.user_id")  #SELECT MY AND FRIENDS TWEETS
    print('TWEETLIST =======__________________________________=====', tweetList)

    tweetTuple = ()
    friendsList.append(session['id'])
    friendsList.append(session['id'])


    for index in range(len(tweetList)):
        if tweetList[index]['follower_user_id'] == session['id'] or tweetList[index]['user_id'] == session['id']:
            friendsList.append(tweetList[index]['followed_user_id'])


    mysql = connectToMySQL("dojo_tweets")
    if len(friendsList):
        tweetTuple = tuple(friendsList)
    else:
        tweetTuple = tuple()

    tweetList2 = mysql.query_db(f"SELECT * FROM tweets WHERE user_id IN {tweetTuple}")

    # tweetList = mysql.query_db(f"SELECT tweets.id, tweets.tweet, tweets.created_at, tweets.updated_at, tweets.user_id, follows.followed_user_id, follows.follower_user_id FROM tweets JOIN users ON tweets.user_id = users.id JOIN follows ON users.id = follows.user_id WHERE tweets.user_id IN {followed_users} GROUP BY tweets.id")



    # get number of likes to display per tweet
    mysql = connectToMySQL("dojo_tweets")
    likesNum = mysql.query_db("SELECT COUNT(id) FROM likes GROUP BY tweet_id")
    print('LIKESNUM=======55555555555555555555555555=====', likesNum)

    return render_template('welcome.html', tweetList = tweetList2, likesNum = likesNum)




@app.route('/tweets/create', methods=['POST', 'GET'])
def tweet_create():

    if request.method == 'GET' or not session['id']:
        return redirect('/')

    # validate tweets here
    incomingTweet = request.form['tweet']
    isValid = True

    if len(incomingTweet) > 255 or len(incomingTweet) < 1:
        isValid = False
        flash("Invalid Tweet, must be between 1 and 255 characters", 'tweet')


    if isValid:
        # enter tweet into database
        mysql = connectToMySQL("dojo_tweets")
        data = {
            'id': session['id'],
            'tweet': incomingTweet
        }
        print('SESSION ID----------*******************************************', session['id'])
        print('TWEET----------*******************************************', incomingTweet)
        query = "INSERT INTO tweets (tweet, user_id) VALUES(%(tweet)s, %(id)s);"
        tweet_add = mysql.query_db(query, data)


    return redirect('/dashboard')




# delete route here
@app.route('/tweets/<id>/delete', methods=['POST'])
def delete_tweet(id):
    print('DELETE ID----------*******************************************', id)
    

    mysql = connectToMySQL("dojo_tweets")
    tweet_check = mysql.query_db(f"SELECT user_id FROM tweets WHERE id={id};")

    print('TWEET CHECK ID----------*******************************************', tweet_check)

    # if userId of tweet = session['id]
    if tweet_check[0]['user_id'] == session['id']:
        mysql = connectToMySQL("dojo_tweets")
        tweet_delete = mysql.query_db(f"DELETE FROM tweets WHERE id={id};")
    else:
        flash('invalid user')

    return redirect('/dashboard')


# edit route here
@app.route('/tweets/<id>/edit', methods=['POST'])
def edit_tweet(id):
    return render_template('edit.html', tweetId = int(id))
    

# update route here
@app.route('/tweets/<id>/update', methods=['POST'])
def update_tweet(id):

    t_id = int(id)
    tweet = request.form['tweet']
    mysql = connectToMySQL("dojo_tweets")
    data = {
        'tweet': tweet,
        'id': t_id
    }
    query = "UPDATE tweets SET tweet = %(tweet)s WHERE id=%(id)s;"
    print('leng request.form tweet55555555555555555555555555555', len(request.form['tweet']))
    if len(request.form['tweet']) < 1 or len(request.form['tweet']) > 255:
        flash('Invalid tweet length')
    else:    
        tweet_edit = mysql.query_db(query, data)
    return redirect('/dashboard')
    






# add like route here
@app.route('/tweets/<id>/like', methods=['POST'])
def like_tweet(id):
    

    # add like to DB
    userId = session['id']
    mysql = connectToMySQL("dojo_tweets")
    tweet_like = mysql.query_db(f"INSERT INTO likes (user_id, tweet_id) VALUES({userId}, {id});")
    print('USER ID----------*******************************************', userId)
    print('TWEET ID----------*******************************************', id)
    return redirect('/dashboard')



# add users route here
@app.route('/users')
def get_users():

    mysql = connectToMySQL("dojo_tweets")
    users = mysql.query_db("SELECT * FROM users;")

    return render_template('/users.html',  users = users)

# add follow to DB

@app.route('/users/<id>/follow')
def follow_user(id):

    mysql = connectToMySQL("dojo_tweets")
    intId = int(id)
    follow = mysql.query_db(f"INSERT INTO follows (followed_user_id, follower_user_id, user_id) VALUES ({intId}, {session['id']}, {session['id']} );")
    print('FOLLOW**********************************************************', )

    return redirect('/dashboard')





if __name__ == "__main__":
    app.run(debug=True)
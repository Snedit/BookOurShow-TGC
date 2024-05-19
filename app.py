from flask import Flask, render_template,request,redirect,url_for, session, jsonify, send_file
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from functools import wraps
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'


mongoKey = os.getenv('mongoClient')

client = MongoClient(mongoKey)
db=client.get_database('BookMyShow')
collection = db.users



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def index():
    # if(session.get("user_id")):
    #     return redirect(url_for('user_index', user_id=session['user_id']))
    # else:
    return render_template('index.html')



@app.route('/<user_id>')
@login_required
def user_index(user_id):
    # Check if the user ID in the session matches the one in the URL
    if session.get('user_id') != user_id:
        return redirect(url_for('index'))
    
    user = collection.find_one({'_id': ObjectId(user_id)})
    print(user)
    if user:
        return render_template('index.html', user=user)
    return render_template('index')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = collection.find_one({'email': email, 'password': password})
        
        if existing_user:
            session['user_id'] = str(existing_user['_id'])  # Store the user_id in the session
            session['show_alert'] = True
            print(str(existing_user['_id']))
            return redirect(url_for('user_index', user_id=session['user_id']))  # Redirect to user_index route with user_id
        else:
            return render_template('login.html', message='Invalid email or password. Please try again.')
            
    return render_template('login.html')

@app.route('/add_points')
@login_required
def add_points():
    user_id = session.get('user_id')
    if user_id:
        # Assuming each click adds 500 points
        collection.update_one({'_id': ObjectId(user_id)}, {'$inc': {'points': 500}})
        return redirect(url_for('user_index', user_id=user_id))
    else:
        return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    existing_user = collection.find_one({'email': email})
    if existing_user:
        message = "User already exists. Please login."
        return render_template('login.html', message=message)
    else:
        logindata = {
            'username': username,
            'phone': phone,
            'email': email,
            'password': password,
            'points': 1000,
        }
        result = collection.insert_one(logindata)
        user_id = str(result.inserted_id)
        session['user_id'] = user_id  # Store the user_id in the session
        print(f"Name: {username}, Phone: {phone}, Email: {email}, Password: {password}")
        return redirect(url_for('user_index', user_id=user_id))
    


if __name__ == "__main__":
    app.run(debug=True)

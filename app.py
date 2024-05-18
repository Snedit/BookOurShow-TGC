from flask import Flask, render_template,request,redirect,url_for, session, jsonify, send_file
from pymongo import MongoClient


app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db=client.get_database('Bookmyshow')
collection = db['register']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = collection.find_one({'email': email, 'password': password})
        
        if existing_user:
            return redirect(url_for('index'),email=email)
        else:
            return render_template('login.html', message='Invalid email or password. Please try again.')
            
    return render_template('login.html') 


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    existing_user = collection.find_one({'email': email})
    if existing_user:
            message = "User already exists. Please login."
            return render_template('login.html', message=message)
    else:
            logindata={
                'username': username,
                'phone': phone,
                'email': email, 
                'password': password,
                'points':1000,
            }
            collection.insert_one(logindata)
            print(f"Name: {username}, Phone: {phone}, Email: {email}, Password: {password}")
            return render_template('login.html')
if __name__ == "__main__":
    app.run(debug=True)

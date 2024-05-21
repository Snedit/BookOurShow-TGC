import datetime
from PIL import Image, ImageDraw, ImageFont
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
    if user and user['points'] < 500:
            return render_template('index.html', user=user, recharge_message="Your points balance is low. Please recharge to continue booking.")
    else:
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
            print(str(existing_user['_id']))
            return redirect(url_for('user_index', user_id=session['user_id']))  # Redirect to user_index route with user_id
        else:
            return render_template('login.html', message='Invalid email or password. Please try again.')
            
    return render_template('login.html')


@app.route('/add_points', methods=['POST'])
def add_points():
    if 'user_id' in session:
        user_id = session['user_id']
        points_to_add = int(request.form['points'])
        
        # Update user points in the database
        user = collection.find_one({'_id': ObjectId(user_id)})
        if user:
            new_points = user['points'] + points_to_add
            collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'points': new_points}})
            return jsonify(success=True, newPoints=new_points)
        else:
            return jsonify(success=False), 400
    else:
        return jsonify(success=False), 401



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
    



@app.route('/user-details')
@login_required
def user_details():
    if 'user_id' in session:
        user_id = session['user_id']
        user = collection.find_one({'_id': ObjectId(user_id)}, {'password': 0})  # Exclude the password from the result
        if user:
            user_details = {
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'points': user['points']
            }
            return jsonify({'user': user_details})
    return jsonify({'error': 'User not logged in'}), 401



@app.route('/confirm_booking', methods=['POST'])
@login_required
def confirm_booking():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    data = request.json
    title = data.get('title')
    detail = data.get('detail')
    ticket_cost = data.get('ticketCost')
    ticket_count = data.get('ticketCount')
    poster = data.get('poster')

    if not title or not detail or not ticket_cost or not ticket_count:
        return jsonify({'success': False, 'message': 'Invalid booking details.'}), 400

    total_cost = int(ticket_cost * ticket_count)

    user = collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    current_points = int(user['points'])
    print("current points ", current_points)
    print("total ", total_cost)
    if current_points < total_cost:
        return jsonify({'success': False, 'message': 'Insufficient points.'}), 400

    new_points = current_points - total_cost
    collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'points': new_points}}
    )

    booking_details = {
        'user_id': ObjectId(user_id),
        'title': title,
        'detail': detail,
        'ticket_count': ticket_count,
        'total_cost': total_cost,
        'timestamp': datetime.datetime.now(),
        'poster':poster
    }
    db.booking.insert_one(booking_details)

    return jsonify({'success': True, 'message': 'Booking confirmed!', 'newPoints': new_points})


@app.route('/booking_history', methods=['GET'])
def booking_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    bookings = list(db.booking.find({'user_id': ObjectId(user_id)}))
    print(bookings)
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        booking['user_id'] = str(booking['user_id'])
        booking['timestamp'] = booking['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({'success': True, 'bookings': bookings})


@app.route('/generate_ticket', methods=['POST'])
@login_required
def generate_ticket():
    data = request.json
    title = data.get('title')
    detail = data.get('detail')
    ticket_count = data.get('ticketCount')
    total_cost = data.get('totalCost')
    user = collection.find_one({'_id': ObjectId(session['user_id'])})
    print("user")
    # Load the ticket image from the static folder
    img = Image.open("ticket.png")
    draw = ImageDraw.Draw(img)
    
    # Use default font
    font = ImageFont.truetype('arial.ttf', 18)

    text_color = (0,0,0)

    text_position = [
        (150, 100, f"Name: {user['username']}"),
        (150, 125, f"Phone: +91 {user['phone']}"),
        (150, 150, f"Email: {user['email']}"),
        (150, 175, f"Movie: {title}"),
        (150, 200, f"Details: {detail}"),
        (150, 225, f"Tickets: {ticket_count}"),
        (150, 250, f"Total Cost: ₹{total_cost}")
    ]
    
    for pos in text_position:
        draw.text((pos[0], pos[1]), pos[2], fill=text_color, font=font)
    
    # Save the image
    output_path = ('static/generated_ticket.png')
    img.save(output_path)

    return send_file(output_path, as_attachment=True, mimetype='image/png')



if __name__ == "__main__":
    app.run()





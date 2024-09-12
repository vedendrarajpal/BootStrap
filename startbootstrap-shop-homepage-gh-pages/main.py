from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql as sql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def db_connect():
    conn = sql.connect(host='localhost', port=3306, user='root', password='', database='flask')
    cur = conn.cursor()
    return conn, cur

# Dummy product data (this can be fetched from the database in a real application)
products = [
    {"id": 1, "name": "Fancy Product", "price": 40.00, "image": "po1.jpg"},
    {"id": 2, "name": "Special Item", "price": 18.00, "image": "po2.jpg", "sale": True},
    {"id": 3, "name": "Sale Item", "price": 25.00, "image": "po3.jpg", "sale": True},
    {"id": 4, "name": "Popular Item", "price": 40.00, "image": "po4.jpg"},
    {"id": 5, "name": "Sale Item", "price": 25.00, "image": "po5.jpg", "sale": True},
    {"id": 6, "name": "Fancy Product", "price": 120.00, "image": "po6.jpg"},
    {"id": 7, "name": "Special Item", "price": 18.00, "image": "po7.jpg", "sale": True},
    {"id": 8, "name": "Popular Item", "price": 40.00, "image": "po8.jpg"},
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/signup/')
def signup():
    return render_template('signup.html')

@app.route('/aftersignup/', methods=['GET', 'POST'])
def aftersignup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Establish database connection
        conn, cur = db_connect()
        
        # Check if the email already exists
        cur.execute("SELECT * FROM data WHERE email = %s", (email,))
        data = cur.fetchone()  # Fetch a single row
        
        if data:
            msg = "Email already exists"
            cur.close()
            conn.close()
            return render_template('signup.html', m=msg)
        else:
            # Hash the password before storing
            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO data (email, password) VALUES (%s, %s)", (email, hashed_password))
            conn.commit()
            ms = "Account successfully created"
            cur.close()
            conn.close()
            return render_template('signup.html', m2=ms)
    else:
        return render_template('signup.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/shop/')
def shop():
    return render_template('shop.html', products=products)
    

@app.route('/cart/')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    # Find the product by ID
    product = next((item for item in products if item['id'] == product_id), None)
    
    if product:
        cart = session.get('cart', [])
        existing_product = next((item for item in cart if item['id'] == product_id), None)
        
        if existing_product:
            existing_product['quantity'] += quantity
        else:
            cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'image': product['image']
            })
        
        session['cart'] = cart
    
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/clear-cart/', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)

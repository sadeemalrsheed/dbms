from flask import Flask, render_template, request, redirect, session
import mysql.connector
from config import DB_CONFIG
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user_id = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE Email=%s AND User_ID=%s AND User_type='Customer'", (email, user_id))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = user[0]
            session['cart'] = []  # clear cart when user logs in
            return redirect('/products')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uid = request.form['id']
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO User (User_ID, Name, Address, Email, User_type) VALUES (%s, %s, %s, %s, 'Customer')",
                           (uid, name, address, email))
            # Insert into Customer table with default 0 loyalty points
            cursor.execute("INSERT INTO Customer (User_ID) VALUES (%s)", (uid,))

            conn.commit()
            return redirect('/')
        except:
            return render_template('register.html', error="Registration failed.")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/products')
def products():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cursor = conn.cursor()

    category = request.args.get('category')
    if category:
        cursor.execute("SELECT Product_ID, Name, Price, Category FROM Product WHERE Category=%s", (category,))
    else:
        cursor.execute("SELECT Product_ID, Name, Price, Category FROM Product")

    product_data = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=product_data, cart=session.get('cart', []))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Product_ID, Name, Price FROM Product WHERE Product_ID = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        # Check if product is already in cart
        for item in session['cart']:
            if item['id'] == product[0]:
                item['quantity'] += 1
                break
        else:
            session['cart'].append({
                'id': product[0],
                'name': product[1],
                'price': float(product[2]),
                'quantity': 1
            })
        session.modified = True

    return redirect('/products')

@app.route('/cart')
def cart():
    cart_items = [item for item in session.get('cart', []) if isinstance(item, dict)]
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    session['cart'] = [item for item in session.get('cart', []) if isinstance(item, dict) and item.get('id') != product_id]
    session.modified = True
    return redirect('/cart')

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session or 'cart' not in session:
        return redirect('/')

    cart_items = session['cart']
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Insert order into Orders table
        cursor.execute("INSERT INTO Orders (User_ID, Order_date, Status, Total_Amount) VALUES (%s, %s, %s, %s)", 
               (session['user'], datetime.now(), 'Placed', total))
        
        # Add 10 loyalty points to the user
        cursor.execute("UPDATE Customer SET Loyalty_points = Loyalty_points + 10 WHERE User_ID = %s", (session['user'],))


        conn.commit()
        session.pop('cart', None)  # Clear the cart after placing order
        return redirect('/products')
    except Exception as e:
        return f"Failed to place order: {str(e)}"
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)



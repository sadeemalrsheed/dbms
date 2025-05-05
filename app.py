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
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM User 
            WHERE Email=%s AND Password=SHA2(%s, 256) AND User_type='Customer'
        """, (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = user[0]  # User_ID
            session['cart'] = []
            return redirect('/products')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO User (Name, Address, Email, Password, User_type)
                VALUES (%s, %s, %s, SHA2(%s, 256), 'Customer')
            """, (name, address, email, password))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO Customer (User_ID) VALUES (%s)", (user_id,))
            cursor.execute("INSERT INTO User_PhoneNum (User_ID, UPhone_num) VALUES (%s, %s)", (user_id, phone))
            conn.commit()
            return redirect('/')
        except Exception as e:
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
    session['cart'] = [item for item in session.get('cart', []) if item.get('id') != product_id]
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
        cursor.execute("""
            INSERT INTO Orders (User_ID, Order_date, Status, Total_Amount)
            VALUES (%s, %s, %s, %s)
        """, (session['user'], datetime.now(), 'Placed', total))

        cursor.execute("UPDATE Customer SET Loyalty_points = Loyalty_points + 10 WHERE User_ID = %s", (session['user'],))
        conn.commit()
        session.pop('cart', None)
        return redirect('/products')
    except Exception as e:
        return f"Failed to place order: {str(e)}"
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

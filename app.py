from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# Ensure cart exists for all users
@app.before_request
def setup_cart():
    if 'cart' not in session:
        session['cart'] = []


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

    # Category filter
    category = request.args.get('category')
    if category:
        cursor.execute("SELECT Product_ID, Name, Price, Category FROM Product WHERE Category=%s LIMIT 3", (category,))
    else:
        cursor.execute("SELECT Product_ID, Name, Price, Category FROM Product")

    product_data = cursor.fetchall()
    conn.close()

    return render_template('products.html', products=product_data, cart=session.get('cart', []))


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    found = False
    for item in session['cart']:
        if item['id'] == product_id:
            item['quantity'] += 1
            found = True
            break
    if not found:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Product_ID, Name, Price FROM Product WHERE Product_ID=%s", (product_id,))
        prod = cursor.fetchone()
        conn.close()
        if prod:
            session['cart'].append({
                'id': prod[0],
                'name': prod[1],
                'price': float(prod[2]),
                'quantity': 1
            })
    session.modified = True
    return redirect('/products')


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
    session.modified = True
    return redirect('/cart')


@app.route('/cart')
def cart():
    total = sum(item['price'] * item['quantity'] for item in session['cart'])
    return render_template('cart.html', cart=session['cart'], total_price=round(total, 2))


if __name__ == '__main__':
    app.run(debug=True)


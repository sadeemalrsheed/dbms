from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from config import DB_CONFIG

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
            session['cart'] = []
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

@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cursor = conn.cursor()
    selected_category = request.args.get('category')
    if selected_category:
        cursor.execute("SELECT Product_ID, Name, Price, Category FROM Product WHERE Category=%s", (selected_category,))
    else:
        cursor.execute("SELECT Product_ID, Name, Price, Category FROM Product LIMIT 9")
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products, cart=session.get('cart', []))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    return redirect('/products')

@app.route('/cart')
def cart():
    return f"Items in Cart: {session.get('cart', [])}"
    
if __name__ == '__main__':
    app.run(debug=True)

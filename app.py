from flask import Flask, render_template, request, redirect, session
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
    categories = ['Books', 'Electronics', 'Clothing']
    product_data = {}
    for cat in categories:
        cursor.execute("SELECT Name, Price FROM Product WHERE Category=%s LIMIT 3", (cat,))
        product_data[cat] = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=product_data)

if __name__ == '__main__':
    app.run(debug=True)

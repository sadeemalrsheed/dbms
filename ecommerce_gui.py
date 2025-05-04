import tkinter as tk
from tkinter import messagebox
import mysql.connector

# MySQL DB connection setup
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",  # empty string
    database="OnlineStoreDB"
)


cursor = db.cursor()

# -----------------------------
# Login & Register Functions
# -----------------------------
def login():
    email = email_entry.get()
    password = password_entry.get()
    cursor.execute("SELECT * FROM User WHERE Email=%s AND User_ID=%s AND User_type='Customer'", (email, password))
    result = cursor.fetchone()
    if result:
        show_products()
    else:
        messagebox.showerror("Error", "Account not found. Please register.")

def register():
    def save_user():
        uid = reg_id.get()
        name = reg_name.get()
        address = reg_address.get()
        email = reg_email.get()
        password = reg_pass.get()
        try:
            cursor.execute("INSERT INTO User (User_ID, Name, Address, Email, User_type) VALUES (%s, %s, %s, %s, 'Customer')", 
                           (uid, name, address, email))
            db.commit()
            messagebox.showinfo("Success", "Account created. Please log in.")
            register_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register: {e}")

    register_window = tk.Toplevel(root)
    register_window.title("Create Account")
    register_window.geometry("300x300")
    tk.Label(register_window, text="ID").pack()
    reg_id = tk.Entry(register_window); reg_id.pack()
    tk.Label(register_window, text="Name").pack()
    reg_name = tk.Entry(register_window); reg_name.pack()
    tk.Label(register_window, text="Address").pack()
    reg_address = tk.Entry(register_window); reg_address.pack()
    tk.Label(register_window, text="Email").pack()
    reg_email = tk.Entry(register_window); reg_email.pack()
    tk.Label(register_window, text="Password").pack()
    reg_pass = tk.Entry(register_window, show="*"); reg_pass.pack()
    tk.Button(register_window, text="Register", command=save_user).pack(pady=10)

# -----------------------------
# Product View Function
# -----------------------------
def show_products():
    prod_win = tk.Toplevel(root)
    prod_win.title("Available Products")
    prod_win.geometry("600x400")

    label = tk.Label(prod_win, text="Product List", font=("Arial", 16), fg="white", bg="#1E90FF")
    label.pack(fill=tk.X)

    categories = ['Books', 'Electronics', 'Clothing']
    for cat in categories:
        tk.Label(prod_win, text=f"{cat}:", font=("Arial", 12, 'bold')).pack()
        cursor.execute("SELECT Name, Price FROM Product WHERE Category=%s LIMIT 3", (cat,))
        for name, price in cursor.fetchall():
            tk.Label(prod_win, text=f" - {name} - {price} SAR").pack()

# -----------------------------
# Main Window
# -----------------------------
root = tk.Tk()
root.title("E-Commerce Login")
root.geometry("400x300")
root.configure(bg="#F0F8FF")

tk.Label(root, text="Login", font=("Arial", 18), bg="#F0F8FF").pack(pady=10)
tk.Label(root, text="Email:", bg="#F0F8FF").pack()
email_entry = tk.Entry(root); email_entry.pack()
tk.Label(root, text="Password:", bg="#F0F8FF").pack()
password_entry = tk.Entry(root, show="*"); password_entry.pack()

tk.Button(root, text="Login", bg="#1E90FF", fg="white", command=login).pack(pady=5)
tk.Button(root, text="Create New Account", command=register).pack()

root.mainloop()

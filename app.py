from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Buat tabel "customers" jika belum ada
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        alamat TEXT NOT NULL,
        password TEXT NOT NULL,
        shift INTEGER NOT NULL
    )
''')

# Fungsi untuk membuka koneksi database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

# Fungsi untuk menutup koneksi database
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(e):
    close_db()

# Fungsi Caesar Cipher
def caesarEncrypt(password, shift):
    encrypted_password = ""
    for char in password:
        if char.isalpha():
            is_upper = char.isupper()
            char = char.lower()
            encrypted_char = chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))
            if is_upper:
                encrypted_char = encrypted_char.upper()
            encrypted_password += encrypted_char
        else:
            encrypted_password += char
    return encrypted_password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nama = request.form['nama']
    alamat = request.form['alamat']
    password = request.form['password']
    shift = int(request.form['shift'])
    encrypted_password = caesarEncrypt(password, shift)

    # Simpan data ke database SQLite3
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO customers (nama, alamat, password, shift) VALUES (?, ?, ?, ?)',
                   (nama, alamat, encrypted_password, shift))
    db.commit()

    return redirect(url_for('customer_list'))

@app.route('/customer_list')
def customer_list():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    return render_template('customer_list.html', customers=customers)

@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM customers WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('customer_list'))


if __name__ == '__main__':
    app.run(debug=True)

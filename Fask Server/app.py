from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Change to your MySQL username
    'password': 'Gautam5@1$',  # Change to your MySQL password
    'database': 'bazaar_db'
}

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
    
    @staticmethod
    def get_by_id(user_id):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, email 
                FROM users 
                WHERE id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return User(
                    user_id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email']
                )
            return None
        except Error as e:
            print(f"Error fetching user by ID: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, email 
                FROM users 
                WHERE email = %s
            """, (email,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return User(
                    user_id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email']
                )
            return None
        except Error as e:
            print(f"Error fetching user by email: {e}")
            return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

def init_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(255),
                category VARCHAR(50)
            )
        """)
        
        # Create cart table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Create wishlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database tables created successfully")
    except Error as e:
        print(f"Error creating database tables: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Attempting login for email: {email}")
        
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Fetch user data from users table using email
            cursor.execute("""
                SELECT id, username, email, password_hash 
                FROM users 
                WHERE email = %s
            """, (email,))
            
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                print(f"User found: {user_data['email']}")
                # Verify password
                if check_password_hash(user_data['password_hash'], password):
                    print(f"Password verified for user: {user_data['email']}")
                    # Create User object
                    user = User(
                        user_id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email']
                    )
                    # Login the user
                    login_user(user)
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('index'))
                else:
                    print(f"Invalid password for user: {email}")
                    flash('Invalid password', 'error')
            else:
                print(f"User not found with email: {email}")
                flash('User not found', 'error')
                
        except Error as e:
            print(f"Database error during login: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                flash('Username or email already exists', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('register'))
            
            # Create new user
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            print(f"Error during registration: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, c.quantity 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """, (current_user.id,))
        cart_items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('cart.html', cart_items=cart_items)
    except Error as e:
        print(f"Error fetching cart items: {e}")
        flash('An error occurred while loading your cart', 'error')
        return redirect(url_for('index'))

@app.route('/wishlist')
@login_required
def wishlist():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.* 
            FROM wishlist w 
            JOIN products p ON w.product_id = p.id 
            WHERE w.user_id = %s
        """, (current_user.id,))
        wishlist_items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('wishlist.html', wishlist_items=wishlist_items)
    except Error as e:
        print(f"Error fetching wishlist items: {e}")
        flash('An error occurred while loading your wishlist', 'error')
        return redirect(url_for('index'))

@app.route('/fashion')
def fashion():
    # Sample fashion products data - in a real application, this would come from a database
    products = [
        {
            'id': 1,
            'name': 'Casual Cotton T-Shirt',
            'price': 29.99,
            'image': 'Assests/product1.jpg',
            'category': 'Men',
            'rating': 4.5,
            'badge': 'new'
        },
        {
            'id': 2,
            'name': 'Floral Summer Dress',
            'price': 49.99,
            'image': 'Assests/product2.jpg',
            'category': 'Women',
            'rating': 4.8,
            'badge': 'trending'
        },
        {
            'id': 3,
            'name': 'Slim Fit Denim Jeans',
            'price': 59.99,
            'image': 'Assests/product3.jpg',
            'category': 'Men',
            'rating': 4.3,
            'badge': 'sale'
        },
        {
            'id': 4,
            'name': 'Kids Party Wear Set',
            'price': 39.99,
            'image': 'Assests/product4.jpg',
            'category': 'Kids',
            'rating': 4.7,
            'badge': 'new'
        }
    ]
    return render_template('fashion.html', products=products)

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 
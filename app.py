from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from decimal import Decimal

load_dotenv()

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')
csrf = CSRFProtect(app)

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
        # First connect without database to create it if not exists
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Gautam5@1$'
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS bazaar_db")
        cursor.execute("USE bazaar_db")
        
        # Create users table first (as it's referenced by others)
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
                original_price DECIMAL(10, 2),
                image_url VARCHAR(255),
                category VARCHAR(50),
                stock INT DEFAULT 100,
                rating DECIMAL(3, 1),
                badge VARCHAR(20)
            )
        """)
        
        # Create cart table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                image VARCHAR(255),
                quantity INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        
        # Create wishlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        
        # Check if products table is empty
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        # Only insert sample products if the products table is empty
        if product_count == 0:
            # Fashion products
            fashion_products = [
                ('T-Shirt', 'Comfortable cotton T-shirt', 24.99, 29.99, 'Assests/T_shirt.jpg', 'T-Shirts', 100, 4.5, 'new'),
                ('Jeans pants', 'Stylish denim jeans', 49.99, 59.99, 'Assests/Fashion/Jeans_pants.jpg', 'Jeans', 100, 4.7, 'trending'),
                ('Summer Dress', 'Light and airy summer dress', 39.99, 49.99, 'Assests/Fashion/Summer_Dress.jpg', 'Dresses', 100, 4.8, 'sale'),
                ('Oversized Hoodie', 'Cozy oversized hoodie', 44.99, 54.99, 'Assests/Fashion/Oversized_Hoodie.jpg', 'Hoodies', 100, 4.6, 'new'),
                ('Silk Saree', 'Traditional silk saree', 89.99, 109.99, 'Assests/Fashion/Silk_Saree.webp', 'Sarees', 100, 4.9, 'premium')
            ]
            
            # Insert all products
            cursor.executemany("""
                INSERT INTO products 
                (name, description, price, original_price, image_url, category, stock, rating, badge)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, fashion_products)
            print("Sample products inserted successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables verified successfully")
    except Error as e:
        print(f"Error with database: {e}")
        raise e  # Re-raise the error to see it in the console

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Find user by email - explicitly select all needed fields
            cursor.execute("""
                SELECT id, username, email, password_hash 
                FROM users 
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            # Check if user exists and password is correct
            if user and check_password_hash(user['password_hash'], password):
                user_obj = User(user['id'], user['username'], user['email'])
                login_user(user_obj)
                
                # After successful login, get cart and wishlist counts
                try:
                    conn = mysql.connector.connect(**db_config)
                    cursor = conn.cursor(dictionary=True)
                    
                    # Get cart count
                    cursor.execute("""
                        SELECT COALESCE(SUM(quantity), 0) as cart_count 
                        FROM cart 
                        WHERE user_id = %s
                    """, (user['id'],))
                    cart_result = cursor.fetchone()
                    
                    # Get wishlist count
                    cursor.execute("""
                        SELECT COUNT(*) as wishlist_count 
                        FROM wishlist 
                        WHERE user_id = %s
                    """, (user['id'],))
                    wishlist_result = cursor.fetchone()
                    
                    cursor.close()
                    conn.close()
                    
                    session['cart_count'] = int(cart_result['cart_count']) if cart_result['cart_count'] else 0
                    session['wishlist_count'] = wishlist_result['wishlist_count']
                except Exception as e:
                    print(f"Error getting counts: {e}")
                    session['cart_count'] = 0
                    session['wishlist_count'] = 0
                
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('index'))
            else:
                flash('Invalid email or password', 'error')
        except Error as e:
            print(f"Error during login: {e}")
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
        
        # Get cart items for current user
        cursor.execute("""
            SELECT cart.*, products.stock 
            FROM cart 
            LEFT JOIN products ON cart.product_id = products.id 
            WHERE cart.user_id = %s
        """, (current_user.id,))
        cart_items = cursor.fetchall()
        
        # Convert Decimal prices to float
        for item in cart_items:
            item['price'] = float(item['price'])
        
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        shipping = 10.00 if cart_items else 0  # $10 shipping if cart not empty
        tax = subtotal * 0.13  # 13% tax
        total = subtotal + shipping + tax
        
        cursor.close()
        conn.close()
        
        return render_template('cart.html', 
                             cart_items=cart_items,
                             subtotal="{:.2f}".format(subtotal),
                             shipping="{:.2f}".format(shipping),
                             tax="{:.2f}".format(tax),
                             total="{:.2f}".format(total))
                             
    except Exception as e:
        return str(e)

@app.route('/wishlist')
@login_required
def wishlist():
    try:
        cursor = mysql.connector.connect(**db_config).cursor(dictionary=True)
        cursor.execute('''
            SELECT w.*, p.name, p.price, p.original_price, p.image_url, p.category 
            FROM wishlist w 
            JOIN products p ON w.product_id = p.id 
            WHERE w.user_id = %s
        ''', (current_user.id,))
        wishlist_items = cursor.fetchall()
        cursor.close()
        
        # Convert Decimal to float for JSON serialization
        for item in wishlist_items:
            if isinstance(item['price'], Decimal):
                item['price'] = float(item['price'])
            if isinstance(item['original_price'], Decimal):
                item['original_price'] = float(item['original_price'])
        
        return render_template('wishlist.html', wishlist_items=wishlist_items)
    except Exception as e:
        print(f"Error fetching wishlist: {str(e)}")
        return render_template('wishlist.html', wishlist_items=[])

@app.route('/fashion')
def fashion():
    # Fashion products data
    products = [
        {
            'id': 1,
            'name': 'T-Shirt',
            'price': 24.99,
            'image': 'Assests/T_shirt.jpg',
            'category': 'T-Shirts',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 29.99
        },
        {
            'id': 2,
            'name': 'Jeans pants',
            'price': 49.99,
            'image': 'Assests/Fashion/Jeans_pants.jpg',
            'category': 'Jeans',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 59.99
        },
        {
            'id': 3,
            'name': 'Summer Dress',
            'price': 39.99,
            'image': 'Assests/Fashion/Summer_Dress.jpg',
            'category': 'Dresses',
            'rating': 4.8,
            'badge': 'sale',
            'original_price': 49.99
        },
        {
            'id': 4,
            'name': 'Oversized Hoodie',
            'price': 44.99,
            'image': 'Assests/Fashion/Oversized_Hoodie.jpg',
            'category': 'Hoodies & Sweatshirts',
            'rating': 4.6,
            'badge': 'new',
            'original_price': 54.99
        },
        {
            'id': 5,
            'name': 'Silk Saree',
            'price': 89.99,
            'image': 'Assests/Fashion/Silk_Saree.webp',
            'category': 'Sarees',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 109.99
        },
        {
            'id': 6,
            'name': 'Shirt',
            'price': 34.99,
            'image': 'Assests/Fashion/shirts.jpg',
            'category': 'Formal Shirts',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 44.99
        },
        {
            'id': 7,
            'name': 'Leather Jacket',
            'price': 99.99,
            'image': 'Assests/Fashion/jacket.jpg',
            'category': 'Jackets',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 129.99
        },
        {
            'id': 8,
            'name': 'Cotton Kurta',
            'price': 29.99,
            'image': 'Assests/Fashion/kurta.jpg',
            'category': 'Kurta/Kurti',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 39.99
        },
        {
            'id': 9,
            'name': 'Skirt',
            'price': 34.99,
            'image': 'Assests/Fashion/Skirts.webp',
            'category': 'Skirts',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 44.99
        },
        {
            'id': 10,
            'name': 'Denim Shorts',
            'price': 24.99,
            'image': 'Assests/Fashion/denim_shorts.webp',
            'category': 'Shorts',
            'rating': 4.4,
            'badge': 'trending',
            'original_price': 29.99
        },
        {
            'id': 11,
            'name': 'Blazer',
            'price': 79.99,
            'image': 'Assests/fashion/blaze.jpg',
            'category': 'Blazers',
            'rating': 4.7,
            'badge': 'premium',
            'original_price': 99.99
        },
        {
            'id': 12,
            'name': 'Yoga Pants',
            'price': 29.99,
            'image': 'Assests/Fashion/yoga-pants.webp',
            'category': 'Activewear',
            'rating': 4.8,
            'badge': 'new',
            'original_price': 39.99
        },
        {
            'id': 13,
            'name': 'Lehenga',
            'price': 149.99,
            'image': 'Assests/Fashion/lehenga.jpg',
            'category': 'Ethnic Wear',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 179.99
        },
        {
            'id': 14,
            'name': 'Sunglasses',
            'price': 19.99,
            'image': 'Assests/Fashion/sunglass.webp',
            'category': 'Sunglasses',
            'rating': 4.5,
            'badge': 'sale',
            'original_price': 29.99
        },
        {
            'id': 15,
            'name': 'Leather Belt',
            'price': 14.99,
            'image': 'Assests/Fashion/letherbelt.jpg',
            'category': 'Belts',
            'rating': 4.6,
            'badge': 'new',
            'original_price': 19.99
        },
        {
            'id': 16,
            'name': 'Analog Watch',
            'price': 59.99,
            'image': 'Assests/Fashion/analogWatch.jpeg',
            'category': 'Watches',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 79.99
        }
    ]
    return render_template('fashion.html', products=products)

@app.route('/electronics')
def electronics():
    # Sample fashion products data
    products = [
        {
            'id': 1,
            'name': 'Smartphone',
            'price': 299.99,
            'image': 'Assests/electronics/smartphone.png',
            'category': 'Smartphones',
            'rating': 4.7,
            'badge': 'new',
            'original_price': 349.99
        },
        {
            'id': 2,
            'name': 'Laptop',
            'price': 799.99,
            'image': 'Assests/electronics/laptop.webp',
            'category': 'Laptops',
            'rating': 4.8,
            'badge': 'trending',
            'original_price': 999.99
        },
        {
            'id': 3,
            'name': 'Smartwatch',
            'price': 149.99,
            'image': 'Assests/electronics/smartwatch.webp',
            'category': 'Smartwatches',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 199.99
        },
        {
            'id': 4,
            'name': 'Bluetooth Earphones',
            'price': 49.99,
            'image': 'Assests/electronics/earphone.jpg',
            'category': 'Bluetooth Earphones',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 69.99
        },
        {
            'id': 5,
            'name': 'Power Bank',
            'price': 29.99,
            'image': 'Assests/electronics/powerbank.jpg',
            'category': 'Power Banks',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 39.99
        },
        {
            'id': 6,
            'name': 'LED Television',
            'price': 499.99,
            'image': 'Assests/electronics/television.jpg',
            'category': 'LED Televisions',
            'rating': 4.6,
            'badge': 'trending',
            'original_price': 699.99
        },
        {
            'id': 7,
            'name': 'DSLR Camera',
            'price': 599.99,
            'image': 'Assests/electronics/dslr_camera.jpg',
            'category': 'DSLR Cameras',
            'rating': 4.2,
            'badge': 'sale',
            'original_price': 799.99
        },
        {
            'id': 8,
            'name': 'Tablet',
            'price': 199.99,
            'image': 'Assests/electronics/tablet.webp',
            'category': 'Tablets',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 249.99
        },
        {
            'id': 9,
            'name': 'Wireless Charger',
            'price': 19.99,
            'image': 'Assests/electronics/wireless_charger.webp',
            'category': 'Wireless Chargers',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 29.99
        },
        {
            'id': 10,
            'name': 'Game Console',
            'price': 299.99,
            'image': 'Assests/electronics/game_console.jpg',
            'category': 'Game Consoles',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 399.99
        },
        {
            'id': 11,
            'name': 'Printer',
            'price': 99.99,
            'image': 'Assests/electronics/printer.jpg',
            'category': 'Printers',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 129.99
        },
        {
            'id': 12,
            'name': 'Bluetooth Speaker',
            'price': 39.99,
            'image': 'Assests/electronics/speaker.webp',
            'category': 'Bluetooth Speakers',
            'rating': 4.4,
            'badge': 'new',
            'original_price': 49.99
        },
        {
            'id': 13,
            'name': 'Monitor',
            'price': 149.99,
            'image': 'Assests/electronics/monitor.webp',
            'category': 'Monitors',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 199.99
        },
        {
            'id': 14,
            'name': 'Router',
            'price': 59.99,
            'image': 'Assests/electronics/router.jpg',
            'category': 'Routers',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 79.99
        },
        {
            'id': 15,
            'name': 'Hard Drive',
            'price': 49.99,
            'image': 'Assests/electronics/hard_drive.webp',
            'category': 'External Hard Drives',
            'rating': 4.3,
            'badge': 'sale',
            'original_price': 69.99
        },
        {
            'id': 16,
            'name': 'Smart Home Device',
            'price': 79.99,
            'image': 'Assests/electronics/smartHone.jpg',
            'category': 'Smart Home Devices',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 99.99
        }
    ]
    return render_template('electronics.html', products=products)

@app.route('/sports')
def sports():
    # Sample fashion products data
    products = [
        {
            'id': 1,
            'name': 'Badminton Racket',
            'price': 49.99,
            'image': 'Assests/sports/badminton.webp',
            'category': 'Badminton',
            'rating': 4.7,
            'badge': 'new',
            'original_price': 69.99
        },
        {
            'id': 2,
            'name': 'Cricket Bat',
            'price': 59.99,
            'image': 'Assests/sports/bat.webp',
            'category': 'Cricket',
            'rating': 4.8,
            'badge': 'trending',
            'original_price': 79.99
        },
        {
            'id': 3,
            'name': 'Yoga Mat',
            'price': 29.99,
            'image': 'Assests/sports/yogamats.jpeg',
            'category': 'Yoga',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 39.99
        },
        {
            'id': 4,
            'name': 'Treadmill',
            'price': 299.99,
            'image': 'Assests/sports/treadmil.jpeg',
            'category': 'Fitness',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 399.99
        },
        {
            'id': 5,
            'name': 'Gym Gloves',
            'price': 19.99,
            'image': 'Assests/sports/gymgloves.jpeg',
            'category': 'Fitness',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 29.99
        },
        {
            'id': 6,
            'name': 'Dumbbells',
            'price': 39.99,
            'image': 'Assests/sports/dumbells.webp',
            'category': 'Fitness',
            'rating': 4.6,
            'badge': 'trending',
            'original_price': 49.99
        },
        {
            'id': 7,
            'name': 'Football',
            'price': 19.99,
            'image': 'Assests/sports/football.webp',
            'category': 'Football',
            'rating': 4.2,
            'badge': 'sale',
            'original_price': 29.99
        },
        {
            'id': 8,
            'name': 'Tennis Racket',
            'price': 59.99,
            'image': 'Assests/sports/tennis.jpeg',
            'category': 'Tennis',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 79.99
        },
        {
            'id': 9,
            'name': 'Skipping Rope',
            'price': 9.99,
            'image': 'Assests/sports/skippingropes.jpg',
            'category': 'Fitness',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 14.99
        },
        {
            'id': 10,
            'name': 'Cycling Helmet',
            'price': 29.99,
            'image': 'Assests/sports/helmets.jpg',
            'category': 'Cycling',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 39.99
        },
        {
            'id': 11,
            'name': 'Sports Shoes',
            'price': 59.99,
            'image': 'Assests/sports/sportshoesjpg.jpg',
            'category': 'Footwear',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 79.99
        },
        {
            'id': 12,
            'name': 'Knee Guards',
            'price': 14.99,
            'image': 'Assests/sports/guards.jpg',
            'category': 'Protective Gear',
            'rating': 4.4,
            'badge': 'new',
            'original_price': 19.99
        },
        {
            'id': 13,
            'name': 'Jersey',
            'price': 29.99,
            'image': 'Assests/sports/jerseys.jpg',
            'category': 'Apparel',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 39.99
        },
        {
            'id': 14,
            'name': 'Water Bottle',
            'price': 14.99,
            'image': 'Assests/sports/Bottles.webp',
            'category': 'Accessories',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 19.99
        },
        {
            'id': 15,
            'name': 'Fitness Band',
            'price': 29.99,
            'image': 'Assests/sports/fitnessbands.jpg',
            'category': 'Fitness',
            'rating': 4.3,
            'badge': 'sale',
            'original_price': 39.99
        },
        {
            'id': 16,
            'name': 'Resistance Bands',
            'price': 19.99,
            'image': 'Assests/sports/rbands.jpg',
            'category': 'Fitness',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 29.99
        }
    ]
    return render_template('sports.html', products=products)

@app.route('/footwear')
def footwear():
    # Footwear products data
    products = [
        {
            'id': 1,
            'name': 'Running Shoes',
            'price': 79.99,
            'image': 'Assests/footwear/runningshoes.jpg',
            'category': 'Sports',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 99.99
        },
        {
            'id': 2,
            'name': 'Casual Sneakers',
            'price': 59.99,
            'image': 'Assests/footwear/sneakers.webp',
            'category': 'Casual',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 69.99
        },
        {
            'id': 3,
            'name': 'Formal Leather Shoes',
            'price': 89.99,
            'image': 'Assests/footwear/formalshoes.webp',
            'category': 'Formal',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 109.99
        },
        {
            'id': 4,
            'name': 'Hiking Boots',
            'price': 99.99,
            'image': 'Assests/footwear/boots.webp',
            'category': 'Outdoor',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 129.99
        },
        {
            'id': 5,
            'name': 'Canvas Slip-ons',
            'price': 39.99,
            'image': 'Assests/footwear/canvas.jpg',
            'category': 'Casual',
            'rating': 4.3,
            'badge': 'new',
            'original_price': 49.99
        },
        {
            'id': 6,
            'name': 'Sports Sandals',
            'price': 44.99,
            'image': 'Assests/footwear/sandals.jpeg',
            'category': 'Sports',
            'rating': 4.4,
            'badge': 'trending',
            'original_price': 54.99
        },
        {
            'id': 7,
            'name': 'Dress Boots',
            'price': 94.99,
            'image': 'Assests/footwear/boots.jpg',
            'category': 'Formal',
            'rating': 4.7,
            'badge': 'premium',
            'original_price': 119.99
        },
        {
            'id': 8,
            'name': 'Walking Shoes',
            'price': 69.99,
            'image': 'Assests/footwear/walking.jpg',
            'category': 'Casual',
            'rating': 4.5,
            'badge': 'sale',
            'original_price': 84.99
        },
        {
            'id': 9,
            'name': 'Basketball Shoes',
            'price': 109.99,
            'image': 'Assests/footwear/basketball.jpg',
            'category': 'Sports',
            'rating': 4.8,
            'badge': 'new',
            'original_price': 139.99
        },
        {
            'id': 10,
            'name': 'Loafers',
            'price': 74.99,
            'image': 'Assests/footwear/loafers.jpg',
            'category': 'Formal',
            'rating': 4.6,
            'badge': 'trending',
            'original_price': 89.99
        },
        {
            'id': 11,
            'name': 'Tennis Shoes',
            'price': 84.99,
            'image': 'Assests/footwear/tennis.jpg',
            'category': 'Sports',
            'rating': 4.5,
            'badge': 'premium',
            'original_price': 99.99
        },
        {
            'id': 12,
            'name': 'Flip Flops',
            'price': 24.99,
            'image': 'Assests/footwear/flipflops.jpg',
            'category': 'Casual',
            'rating': 4.2,
            'badge': 'sale',
            'original_price': 29.99
        },
        {
            'id': 13,
            'name': 'Golf Shoes',
            'price': 119.99,
            'image': 'Assests/footwear/golf.jpg',
            'category': 'Sports',
            'rating': 4.7,
            'badge': 'new',
            'original_price': 149.99
        },
        {
            'id': 14,
            'name': 'Oxford Shoes',
            'price': 99.99,
            'image': 'Assests/footwear/oxford.jpg',
            'category': 'Formal',
            'rating': 4.8,
            'badge': 'trending',
            'original_price': 124.99
        },
        {
            'id': 15,
            'name': 'Trail Running Shoes',
            'price': 89.99,
            'image': 'Assests/footwear/trail.jpg',
            'category': 'Outdoor',
            'rating': 4.6,
            'badge': 'premium',
            'original_price': 109.99
        },
        {
            'id': 16,
            'name': 'Boat Shoes',
            'price': 64.99,
            'image': 'Assests/footwear/boat.jpg',
            'category': 'Casual',
            'rating': 4.4,
            'badge': 'sale',
            'original_price': 79.99
        }
    ]
    return render_template('footwear.html', products=products)

@app.route('/groceries')
def groceries():
    # Grocery products data
    products = [
        {
            'id': 1,
            'name': 'Organic Bananas',
            'price': 2.99,
            'image': 'Assests/groceries/bananas.jpg',
            'category': 'Fruits',
            'rating': 4.8,
            'badge': 'organic',
            'original_price': 3.49
        },
        {
            'id': 2,
            'name': 'Whole Grain Bread',
            'price': 3.49,
            'image': 'Assests/groceries/bread.jpg',
            'category': 'Bakery',
            'rating': 4.6,
            'badge': 'fresh',
            'original_price': 3.99
        },
        {
            'id': 3,
            'name': 'Farm Fresh Eggs',
            'price': 4.99,
            'image': 'Assests/groceries/eggs.jpg',
            'category': 'Dairy',
            'rating': 4.7,
            'badge': 'farm-fresh',
            'original_price': 5.49
        },
        {
            'id': 4,
            'name': 'Organic Milk',
            'price': 3.99,
            'image': 'Assests/groceries/milk.jpg',
            'category': 'Dairy',
            'rating': 4.5,
            'badge': 'organic',
            'original_price': 4.49
        },
        {
            'id': 5,
            'name': 'Fresh Tomatoes',
            'price': 2.49,
            'image': 'Assests/groceries/tomatoes.jpg',
            'category': 'Vegetables',
            'rating': 4.4,
            'badge': 'fresh',
            'original_price': 2.99
        },
        {
            'id': 6,
            'name': 'Chicken Breast',
            'price': 8.99,
            'image': 'Assests/groceries/chicken.jpg',
            'category': 'Meat',
            'rating': 4.6,
            'badge': 'premium',
            'original_price': 10.99
        },
        {
            'id': 7,
            'name': 'Basmati Rice',
            'price': 6.99,
            'image': 'Assests/groceries/rice.jpg',
            'category': 'Grains',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 7.99
        },
        {
            'id': 8,
            'name': 'Mixed Vegetables',
            'price': 3.99,
            'image': 'Assests/groceries/mixed-veg.jpg',
            'category': 'Frozen',
            'rating': 4.3,
            'badge': 'sale',
            'original_price': 4.99
        },
        {
            'id': 9,
            'name': 'Greek Yogurt',
            'price': 4.49,
            'image': 'Assests/groceries/yogurt.jpg',
            'category': 'Dairy',
            'rating': 4.7,
            'badge': 'healthy',
            'original_price': 4.99
        },
        {
            'id': 10,
            'name': 'Fresh Apples',
            'price': 3.99,
            'image': 'Assests/groceries/apples.jpg',
            'category': 'Fruits',
            'rating': 4.5,
            'badge': 'fresh',
            'original_price': 4.49
        },
        {
            'id': 11,
            'name': 'Pasta',
            'price': 1.99,
            'image': 'Assests/groceries/pasta.jpg',
            'category': 'Grains',
            'rating': 4.4,
            'badge': 'sale',
            'original_price': 2.49
        },
        {
            'id': 12,
            'name': 'Olive Oil',
            'price': 7.99,
            'image': 'Assests/groceries/olive-oil.jpg',
            'category': 'Cooking',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 9.99
        },
        {
            'id': 13,
            'name': 'Fresh Salmon',
            'price': 12.99,
            'image': 'Assests/groceries/salmon.jpg',
            'category': 'Seafood',
            'rating': 4.6,
            'badge': 'premium',
            'original_price': 14.99
        },
        {
            'id': 14,
            'name': 'Organic Spinach',
            'price': 3.49,
            'image': 'Assests/groceries/spinach.jpg',
            'category': 'Vegetables',
            'rating': 4.5,
            'badge': 'organic',
            'original_price': 3.99
        },
        {
            'id': 15,
            'name': 'Cheese Block',
            'price': 5.99,
            'image': 'Assests/groceries/cheese.jpg',
            'category': 'Dairy',
            'rating': 4.7,
            'badge': 'fresh',
            'original_price': 6.99
        },
        {
            'id': 16,
            'name': 'Mixed Nuts',
            'price': 8.99,
            'image': 'Assests/groceries/nuts.jpg',
            'category': 'Snacks',
            'rating': 4.6,
            'badge': 'healthy',
            'original_price': 9.99
        }
    ]
    return render_template('groceries.html', products=products)

@app.route('/beauty')
def beauty():
    # Sample fashion products data
    products = [
        {
            'id': 1,
            'name': 'Face Wash',
            'price': 9.99,
            'image': 'Assests/beauty/facewash.jpg',
            'category': 'Skincare',
            'rating': 4.7,
            'badge': 'new',
            'original_price': 14.99
        },
        {
            'id': 2,
            'name': 'Lipsticks',
            'price': 7.99,
            'image': 'Assests/beauty/lipstick.jpg',
            'category': 'Makeup',
            'rating': 4.8,
            'badge': 'trending',
            'original_price': 12.99
        },
        {
            'id': 3,
            'name': 'Foundation',
            'price': 14.99,
            'image': 'Assests/beauty/foundation.jpg',
            'category': 'Makeup',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 19.99
        },
        {
            'id': 4,
            'name': 'Compact Powder',
            'price': 8.99,
            'image': 'Assests/beauty/compact.jpg',
            'category': 'Makeup',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 12.99
        },
        {
            'id': 5,
            'name': 'Kajal',
            'price': 6.99,
            'image': 'Assests/beauty/kajal.jpg',
            'category': 'Makeup',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 9.99
        },
        {
            'id': 6,
            'name': 'Eyeliners',
            'price': 7.49,
            'image': 'Assests/beauty/eyeliner.jpg',
            'category': 'Makeup',
            'rating': 4.6,
            'badge': 'trending',
            'original_price': 11.49
        },
        {
            'id': 7,
            'name': 'Face Serum',
            'price': 12.99,
            'image': 'Assests/beauty/serum.jpg',
            'category': 'Skincare',
            'rating': 4.2,
            'badge': 'sale',
            'original_price': 17.99
        },
        {
            'id': 8,
            'name': 'Face Masks',
            'price': 11.99,
            'image': 'Assests/beauty/facemask.jpg',
            'category': 'Skincare',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 15.99
        },
        {
            'id': 9,
            'name': 'Nail Polish',
            'price': 4.99,
            'image': 'Assests/beauty/nailpolish.jpg',
            'category': 'Nails',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 6.99
        },
        {
            'id': 10,
            'name': 'Perfumes',
            'price': 29.99,
            'image': 'Assests/beauty/perfume.jpg',
            'category': 'Fragrance',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 39.99
        },
        {
            'id': 11,
            'name': 'Body Lotion',
            'price': 12.99,
            'image': 'Assests/beauty/lotion.jpg',
            'category': 'Skincare',
            'rating': 4.6,
            'badge': 'sale',
            'original_price': 17.99
        },
        {
            'id': 12,
            'name': 'Hair Serum',
            'price': 10.99,
            'image': 'Assests/beauty/hairserum.jpg',
            'category': 'Haircare',
            'rating': 4.4,
            'badge': 'new',
            'original_price': 14.99
        },
        {
            'id': 13,
            'name': 'Shampoo',
            'price': 8.99,
            'image': 'Assests/beauty/shampoo.jpg',
            'category': 'Haircare',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 12.99
        },
        {
            'id': 14,
            'name': 'Conditioner',
            'price': 9.99,
            'image': 'Assests/beauty/conditioner.jpg',
            'category': 'Haircare',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 14.99
        },
        {
            'id': 15,
            'name': 'Sunscreen',
            'price': 11.99,
            'image': 'Assests/beauty/sunscreen.jpg',
            'category': 'Skincare',
            'rating': 4.3,
            'badge': 'sale',
            'original_price': 16.99
        },
        {
            'id': 16,
            'name': 'Makeup Remover',
            'price': 7.99,
            'image': 'Assests/beauty/remover.jpg',
            'category': 'Makeup',
            'rating': 4.5,
            'badge': 'new',
            'original_price': 11.99
        }
    ]
    return render_template('beauty.html', products=products)

@app.route('/health')
def health():
    # Health products data
    products = [
        {
            'id': 1,
            'name': 'Multivitamin Tablets',
            'price': 24.99,
            'image': 'Assests/health/multivitamin.jpg',
            'category': 'Vitamins',
            'rating': 4.7,
            'badge': 'premium',
            'original_price': 29.99
        },
        {
            'id': 2,
            'name': 'Protein Powder',
            'price': 39.99,
            'image': 'Assests/health/protein.jpg',
            'category': 'Supplements',
            'rating': 4.8,
            'badge': 'trending',
            'original_price': 49.99
        },
        {
            'id': 3,
            'name': 'Digital BP Monitor',
            'price': 49.99,
            'image': 'Assests/health/bpmonitor.jpg',
            'category': 'Medical Devices',
            'rating': 4.6,
            'badge': 'new',
            'original_price': 59.99
        },
        {
            'id': 4,
            'name': 'First Aid Kit',
            'price': 29.99,
            'image': 'Assests/health/firstaid.jpg',
            'category': 'First Aid',
            'rating': 4.5,
            'badge': 'sale',
            'original_price': 34.99
        },
        {
            'id': 5,
            'name': 'Omega-3 Fish Oil',
            'price': 19.99,
            'image': 'Assests/health/fishoil.jpg',
            'category': 'Supplements',
            'rating': 4.7,
            'badge': 'premium',
            'original_price': 24.99
        },
        {
            'id': 6,
            'name': 'Digital Thermometer',
            'price': 14.99,
            'image': 'Assests/health/thermometer.jpg',
            'category': 'Medical Devices',
            'rating': 4.4,
            'badge': 'new',
            'original_price': 19.99
        },
        {
            'id': 7,
            'name': 'Calcium Supplements',
            'price': 21.99,
            'image': 'Assests/health/calcium.jpg',
            'category': 'Supplements',
            'rating': 4.6,
            'badge': 'trending',
            'original_price': 26.99
        },
        {
            'id': 8,
            'name': 'Glucose Monitor',
            'price': 44.99,
            'image': 'Assests/health/glucose.jpg',
            'category': 'Medical Devices',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 54.99
        },
        {
            'id': 9,
            'name': 'Immunity Booster',
            'price': 29.99,
            'image': 'Assests/health/immunity.jpg',
            'category': 'Supplements',
            'rating': 4.5,
            'badge': 'sale',
            'original_price': 34.99
        },
        {
            'id': 10,
            'name': 'Weighing Scale',
            'price': 34.99,
            'image': 'Assests/health/scale.jpg',
            'category': 'Medical Devices',
            'rating': 4.6,
            'badge': 'new',
            'original_price': 39.99
        },
        {
            'id': 11,
            'name': 'Herbal Tea',
            'price': 16.99,
            'image': 'Assests/health/herbaltea.jpg',
            'category': 'Herbal',
            'rating': 4.4,
            'badge': 'trending',
            'original_price': 19.99
        },
        {
            'id': 12,
            'name': 'Joint Support Tablets',
            'price': 26.99,
            'image': 'Assests/health/jointsupport.jpg',
            'category': 'Supplements',
            'rating': 4.7,
            'badge': 'premium',
            'original_price': 31.99
        },
        {
            'id': 13,
            'name': 'Pulse Oximeter',
            'price': 39.99,
            'image': 'Assests/health/oximeter.jpg',
            'category': 'Medical Devices',
            'rating': 4.8,
            'badge': 'new',
            'original_price': 49.99
        },
        {
            'id': 14,
            'name': 'Digestive Enzymes',
            'price': 22.99,
            'image': 'Assests/health/digestive.jpg',
            'category': 'Supplements',
            'rating': 4.5,
            'badge': 'sale',
            'original_price': 27.99
        },
        {
            'id': 15,
            'name': 'Eye Care Supplements',
            'price': 31.99,
            'image': 'Assests/health/eyecare.jpg',
            'category': 'Supplements',
            'rating': 4.6,
            'badge': 'trending',
            'original_price': 36.99
        },
        {
            'id': 16,
            'name': 'Compression Socks',
            'price': 19.99,
            'image': 'Assests/health/socks.jpg',
            'category': 'Medical Accessories',
            'rating': 4.4,
            'badge': 'new',
            'original_price': 24.99
        }
    ]
    return render_template('health.html', products=products)

@app.route('/jwellery')
def jwellery():
    # Jewellery products data
    products = [
        {
            'id': 1,
            'name': 'Gold Earrings',
            'price': 149.99,
            'image': 'Assests/jewellery/goldearrings.jpeg',
            'category': 'Gold Earrings',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 179.99
        },
        {
            'id': 2,
            'name': 'Diamond Solitaire Ring',
            'price': 499.99,
            'image': 'Assests/jewellery/diamondrings.jpg',
            'category': 'Diamond Rings',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 599.99
        },
        {
            'id': 3,
            'name': 'Pearl Necklace',
            'price': 199.99,
            'image': 'Assests/jewellery/necklace.webp',
            'category': 'Necklaces',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 249.99
        },
        {
            'id': 4,
            'name': 'Gold Bangles Set',
            'price': 299.99,
            'image': 'Assests/jewellery/bangles.jpeg',
            'category': 'Bangles',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 349.99
        },
        {
            'id': 5,
            'name': 'Diamond Nose Pin',
            'price': 79.99,
            'image': 'Assests/jewellery/nosepins.jpeg',
            'category': 'Nose Pins',
            'rating': 4.6,
            'badge': 'new',
            'original_price': 99.99
        },
        {
            'id': 6,
            'name': 'Silver Bracelet',
            'price': 49.99,
            'image': 'Assests/jewellery/bracelet.jpg',
            'category': 'Bracelets',
            'rating': 4.5,
            'badge': 'sale',
            'original_price': 69.99
        },
        {
            'id': 7,
            'name': 'Gold Anklet',
            'price': 89.99,
            'image': 'Assests/jewellery/anklet.jpg',
            'category': 'Anklets',
            'rating': 4.7,
            'badge': 'trending',
            'original_price': 109.99
        },
        {
            'id': 8,
            'name': 'Pendant Set with Chain',
            'price': 159.99,
            'image': 'Assests/jewellery/pendant.jpeg',
            'category': 'Pendant Sets',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 189.99
        },
        {
            'id': 9,
            'name': 'Gold Mangalsutra',
            'price': 399.99,
            'image': 'Assests/jewellery/mangalsutra.jpeg',
            'category': 'Mangalsutra',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 499.99
        },
        {
            'id': 10,
            'name': 'Silver Toe Ring Set',
            'price': 29.99,
            'image': 'Assests/jewellery/toerings.webp',
            'category': 'Toe Rings',
            'rating': 4.4,
            'badge': 'new',
            'original_price': 39.99
        },
        {
            'id': 11,
            'name': 'Temple Jewellery Set',
            'price': 249.99,
            'image': 'Assests/jewellery/temple.jpg',
            'category': 'Temple Jewellery',
            'rating': 4.8,
            'badge': 'premium',
            'original_price': 299.99
        },
        {
            'id': 12,
            'name': 'Artificial Jhumka Earrings',
            'price': 19.99,
            'image': 'Assests/jewellery/artificial.webp',
            'category': 'Artificial Earrings',
            'rating': 4.3,
            'badge': 'sale',
            'original_price': 29.99
        },
        {
            'id': 13,
            'name': 'Silver Chain',
            'price': 39.99,
            'image': 'Assests/jewellery/silver.jpg',
            'category': 'Silver Chains',
            'rating': 4.5,
            'badge': 'trending',
            'original_price': 49.99
        },
        {
            'id': 14,
            'name': 'Diamond Stud Earrings',
            'price': 199.99,
            'image': 'Assests/jewellery/stud.webp',
            'category': 'Stud Earrings',
            'rating': 4.7,
            'badge': 'premium',
            'original_price': 249.99
        },
        {
            'id': 15,
            'name': 'Kundan Necklace Set',
            'price': 179.99,
            'image': 'Assests/jewellery/kundansets.webp',
            'category': 'Kundan Sets',
            'rating': 4.6,
            'badge': 'new',
            'original_price': 219.99
        },
        {
            'id': 16,
            'name': 'Bridal Jewellery Set',
            'price': 599.99,
            'image': 'Assests/jewellery/b.webp',
            'category': 'Bridal Jewellery Sets',
            'rating': 4.9,
            'badge': 'premium',
            'original_price': 699.99
        }
    ]
    return render_template('jwellery.html', products=products)

@app.route('/check-item-status', methods=['POST'])
@login_required
def check_item_status():
    try:
        data = request.get_json()
        
        # Get cart and wishlist counts
        if (data.get('get_counts')):
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Get cart count
            cursor.execute("""
                SELECT COALESCE(SUM(quantity), 0) as cart_count 
                FROM cart 
                WHERE user_id = %s
            """, (current_user.id,))
            cart_result = cursor.fetchone()
            cart_count = float(cart_result['cart_count']) if cart_result['cart_count'] else 0
            
            # Get wishlist count
            cursor.execute("""
                SELECT COUNT(*) as wishlist_count 
                FROM wishlist 
                WHERE user_id = %s
            """, (current_user.id,))
            wishlist_result = cursor.fetchone()
            wishlist_count = wishlist_result['wishlist_count'] if wishlist_result else 0
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'cart_count': cart_count,
                'wishlist_count': wishlist_count
            })
        
        # Check status for specific product
        product_id = int(data.get('product_id'))
        if not product_id:
            return jsonify({
                'success': False,
                'message': 'Product ID is required'
            }), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Check cart status
        cursor.execute("""
            SELECT id, price, quantity 
            FROM cart 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        cart_item = cursor.fetchone()
        in_cart = cart_item is not None
        if cart_item and 'price' in cart_item:
            cart_item['price'] = float(cart_item['price'])

        # Check wishlist status
        cursor.execute("""
            SELECT id 
            FROM wishlist 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        in_wishlist = cursor.fetchone() is not None

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'in_cart': in_cart,
            'in_wishlist': in_wishlist,
            'cart_item': cart_item if in_cart else None
        })

    except Exception as e:
        print(f"Error checking item status: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        data = request.json
        user_id = current_user.id
        product_id = int(data.get('product_id'))
        product_name = data.get('product_name')
        price = float(data.get('price'))
        image = data.get('image')
        quantity = int(data.get('quantity', 1))
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # First verify the product exists and has enough stock
        cursor.execute("""
            SELECT id, name, stock, price 
            FROM products 
            WHERE id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404
            
        # Check if item is already in cart
        cursor.execute("""
            SELECT id, quantity 
            FROM cart 
            WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity if item already exists
            new_quantity = existing_item['quantity'] + quantity
            cursor.execute("""
                UPDATE cart 
                SET quantity = %s 
                WHERE id = %s
            """, (new_quantity, existing_item['id']))
        else:
            # Add new item to cart
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, product_name, price, image, quantity) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, product_id, product_name, price, image, quantity))
        
        conn.commit()
        
        # Get updated cart count and total
        cursor.execute("""
            SELECT 
                CAST(SUM(quantity) AS DECIMAL(10,2)) as cart_count,
                CAST(SUM(price * quantity) AS DECIMAL(10,2)) as cart_total
            FROM cart 
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        
        cart_count = float(result['cart_count']) if result and result['cart_count'] else 0
        cart_total = float(result['cart_total']) if result and result['cart_total'] else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "cart_count": cart_count,
            "cart_total": cart_total,
            "message": "Item added to cart successfully!"
        })
    
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/remove-from-cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Verify the cart item belongs to the current user
        cursor.execute("""
            SELECT id 
            FROM cart 
            WHERE id = %s AND user_id = %s
        """, (cart_id, current_user.id))
        
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'Cart item not found'
            }), 404
        
        # Delete the cart item
        cursor.execute("""
            DELETE FROM cart 
            WHERE id = %s AND user_id = %s
        """, (cart_id, current_user.id))
        
        # Get updated cart count
        cursor.execute("""
            SELECT CAST(SUM(quantity) AS DECIMAL(10,2)) as cart_count 
            FROM cart 
            WHERE user_id = %s
        """, (current_user.id,))
        result = cursor.fetchone()
        cart_count = float(result['cart_count']) if result and result['cart_count'] else 0
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'message': 'Item removed from cart successfully'
        })
        
    except Exception as e:
        print(f"Error removing item from cart: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    try:
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Update quantity
        cursor.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
                      (quantity, current_user.id, product_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/add-to-wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    try:
        data = request.get_json()
        product_id = int(data.get('product_id'))
        
        if not product_id:
            return jsonify({
                'success': False,
                'message': 'Product ID is required'
            }), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # First verify the product exists
        cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404

        # Check if item already exists in wishlist
        cursor.execute("""
            SELECT id FROM wishlist 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # Remove from wishlist if already exists
            cursor.execute("""
                DELETE FROM wishlist 
                WHERE user_id = %s AND product_id = %s
            """, (current_user.id, product_id))
            is_added = False
        else:
            # Add new item to wishlist
            cursor.execute("""
                INSERT INTO wishlist (user_id, product_id) 
                VALUES (%s, %s)
            """, (current_user.id, product_id))
            is_added = True

        # Get updated wishlist count
        cursor.execute("""
            SELECT COUNT(*) as wishlist_count 
            FROM wishlist 
            WHERE user_id = %s
        """, (current_user.id,))
        result = cursor.fetchone()
        wishlist_count = result['wishlist_count'] if result else 0

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'is_added': is_added,
            'wishlist_count': wishlist_count,
            'message': 'Item {} wishlist successfully!'.format('added to' if is_added else 'removed from')
        })

    except Exception as e:
        print(f"Error modifying wishlist: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/remove-from-wishlist/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Delete the item from wishlist
        cursor.execute("""
            DELETE FROM wishlist 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        
        # Get updated wishlist count
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM wishlist 
            WHERE user_id = %s
        """, (current_user.id,))
        wishlist_count = cursor.fetchone()['count']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from wishlist',
            'wishlist_count': wishlist_count
        })
        
    except Exception as e:
        print("Error removing from wishlist:", str(e))
        return jsonify({
            'success': False,
            'message': f'Error removing item from wishlist: {str(e)}'
        }), 500

@app.route('/orders')
@login_required
def orders():
    # For now, return an empty orders list
    # You can later implement the logic to fetch orders from your database
    orders = []
    return render_template('orders.html', orders=orders)

@app.route('/move-to-cart/<int:product_id>', methods=['POST'])
@login_required
def move_to_cart(product_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # First get the product details
        cursor.execute("""
            SELECT p.* 
            FROM products p 
            JOIN wishlist w ON w.product_id = p.id 
            WHERE w.user_id = %s AND w.product_id = %s
        """, (current_user.id, product_id))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found in wishlist'
            }), 404
            
        # Convert Decimal to float for JSON serialization
        if isinstance(product['price'], Decimal):
            product['price'] = float(product['price'])
            
        # Check if item already exists in cart
        cursor.execute("""
            SELECT id, quantity 
            FROM cart 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        existing_cart_item = cursor.fetchone()
        
        if existing_cart_item:
            # Update quantity if already in cart
            cursor.execute("""
                UPDATE cart 
                SET quantity = quantity + 1 
                WHERE id = %s
            """, (existing_cart_item['id'],))
        else:
            # Add new item to cart
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, product_name, price, image, quantity) 
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (current_user.id, product_id, product['name'], product['price'], product['image_url']))
            
        # Remove from wishlist
        cursor.execute("""
            DELETE FROM wishlist 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        
        # Get updated counts
        cursor.execute("""
            SELECT COUNT(*) as wishlist_count 
            FROM wishlist 
            WHERE user_id = %s
        """, (current_user.id,))
        wishlist_count = cursor.fetchone()['wishlist_count']
        
        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0) as cart_count 
            FROM cart 
            WHERE user_id = %s
        """, (current_user.id,))
        cart_count = float(cursor.fetchone()['cart_count'])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Item moved to cart successfully',
            'wishlist_count': wishlist_count,
            'cart_count': cart_count
        })
        
    except Exception as e:
        print("Error moving item to cart:", str(e))
        return jsonify({
            'success': False,
            'message': f'Error moving item to cart: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
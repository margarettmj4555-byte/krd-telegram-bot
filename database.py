"""
Database setup and models for KRD Telegram Shopping Bot
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from config import DB_NAME


class Database:
    """Database manager for the bot"""

    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                emoji TEXT DEFAULT '📦',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_url TEXT,
                stock INTEGER DEFAULT 10,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (category_id)
            )
        """)

        # Cart table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                UNIQUE(user_id, product_id)
            )
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_price REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        # Order Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)

        conn.commit()
        conn.close()

    # ============= USER METHODS =============
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Add a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_user(self, user_id: int, phone: str = None, address: str = None) -> bool:
        """Update user information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if phone:
                cursor.execute("UPDATE users SET phone = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", 
                             (phone, user_id))
            if address:
                cursor.execute("UPDATE users SET address = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", 
                             (address, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """Get all users (for admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ============= CATEGORY METHODS =============
    def add_category(self, name: str, description: str = None, emoji: str = "📦") -> bool:
        """Add a new category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (name, description, emoji)
                VALUES (?, ?, ?)
            """, (name, description, emoji))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding category: {e}")
            return False

    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY category_id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_category(self, category_id: int) -> Optional[Dict]:
        """Get category by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE category_id = ?", (category_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_category(self, category_id: int, name: str = None, description: str = None, emoji: str = None) -> bool:
        """Update category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if name:
                cursor.execute("UPDATE categories SET name = ? WHERE category_id = ?", (name, category_id))
            if description:
                cursor.execute("UPDATE categories SET description = ? WHERE category_id = ?", (description, category_id))
            if emoji:
                cursor.execute("UPDATE categories SET emoji = ? WHERE category_id = ?", (emoji, category_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating category: {e}")
            return False

    def delete_category(self, category_id: int) -> bool:
        """Delete category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False

    # ============= PRODUCT METHODS =============
    def add_product(self, category_id: int, name: str, description: str, price: float, image_url: str = None, stock: int = 10) -> bool:
        """Add a new product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (category_id, name, description, price, image_url, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (category_id, name, description, price, image_url, stock))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding product: {e}")
            return False

    def get_product(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_products_by_category(self, category_id: int) -> List[Dict]:
        """Get products by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM products 
            WHERE category_id = ? AND is_active = 1
            ORDER BY product_id
        """, (category_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_products(self) -> List[Dict]:
        """Get all active products"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY product_id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_product(self, product_id: int, name: str = None, description: str = None, price: float = None, 
                      image_url: str = None, stock: int = None, is_active: bool = None) -> bool:
        """Update product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if name:
                cursor.execute("UPDATE products SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                             (name, product_id))
            if description:
                cursor.execute("UPDATE products SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                             (description, product_id))
            if price:
                cursor.execute("UPDATE products SET price = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                             (price, product_id))
            if image_url:
                cursor.execute("UPDATE products SET image_url = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                             (image_url, product_id))
            if stock is not None:
                cursor.execute("UPDATE products SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                             (stock, product_id))
            if is_active is not None:
                cursor.execute("UPDATE products SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                             (is_active, product_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Delete product (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", 
                         (product_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False

    # ============= CART METHODS =============
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> bool:
        """Add product to cart"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
            """, (user_id, product_id, quantity, quantity))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False

    def get_cart(self, user_id: int) -> List[Dict]:
        """Get user's cart"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, p.name, p.price, p.image_url 
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = ?
            ORDER BY c.added_at
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_cart_item(self, user_id: int, product_id: int, quantity: int) -> bool:
        """Update cart item quantity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if quantity <= 0:
                cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            else:
                cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?", 
                             (quantity, user_id, product_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating cart: {e}")
            return False

    def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        """Remove product from cart"""
        return self.update_cart_item(user_id, product_id, 0)

    def clear_cart(self, user_id: int) -> bool:
        """Clear user's cart"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False

    def get_cart_total(self, user_id: int) -> float:
        """Get cart total price"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(c.quantity * p.price) as total
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row['total'] else 0

    # ============= ORDER METHODS =============
    def create_order(self, user_id: int, total_price: float, notes: str = None) -> Optional[int]:
        """Create a new order"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (user_id, total_price, notes, status)
                VALUES (?, ?, ?, 'pending')
            """, (user_id, total_price, notes))
            conn.commit()
            order_id = cursor.lastrowid
            conn.close()
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    def add_order_item(self, order_id: int, product_id: int, quantity: int, price: float) -> bool:
        """Add item to order"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding order item: {e}")
            return False

    def get_order(self, order_id: int) -> Optional[Dict]:
        """Get order by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_orders(self, user_id: int) -> List[Dict]:
        """Get user's orders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_order_items(self, order_id: int) -> List[Dict]:
        """Get items in an order"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT oi.*, p.name, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, (order_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_orders(self) -> List[Dict]:
        """Get all orders (for admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            """, (status, order_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False


# Initialize database
db = Database()

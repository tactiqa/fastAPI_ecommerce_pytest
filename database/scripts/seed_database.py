#!/usr/bin/env python3
"""
Seed the e-commerce database with realistic fake data
"""

import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from faker import Faker

# Initialize Faker
fake = Faker()

def hash_password(password):
    """Simple password hashing"""
    import bcrypt
    # Encode password and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def seed_database():
    """Seed all tables with fake data"""
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Missing DATABASE_URL in .env file")
        return False
    
    try:
        print("=" * 70)
        print("SEEDING E-COMMERCE DATABASE")
        print("=" * 70)
        
        print("\n🔍 Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Connected successfully!\n")
        
        # ====================================================================
        # 1. SEED CATEGORIES
        # ====================================================================
        print("📁 Seeding Categories...")
        
        # Main categories
        main_categories = [
            ("Electronics", "Electronic devices and accessories"),
            ("Clothing", "Fashion and apparel"),
            ("Home & Garden", "Home improvement and garden supplies"),
            ("Sports & Outdoors", "Sports equipment and outdoor gear"),
            ("Books", "Books and educational materials"),
            ("Toys & Games", "Toys, games, and hobbies"),
            ("Health & Beauty", "Health, beauty, and personal care"),
            ("Food & Beverages", "Food, drinks, and gourmet items")
        ]
        
        category_ids = {}
        
        for name, desc in main_categories:
            cursor.execute("""
                INSERT INTO categories (name, description)
                VALUES (%s, %s)
                RETURNING category_id
            """, (name, desc))
            category_ids[name] = cursor.fetchone()['category_id']
        
        # Subcategories
        subcategories = {
            "Electronics": ["Smartphones", "Laptops", "Tablets", "Cameras", "Audio"],
            "Clothing": ["Men's Wear", "Women's Wear", "Kids' Wear", "Shoes", "Accessories"],
            "Home & Garden": ["Furniture", "Kitchen", "Bathroom", "Garden Tools", "Decor"],
            "Sports & Outdoors": ["Fitness", "Camping", "Cycling", "Team Sports", "Water Sports"],
            "Books": ["Fiction", "Non-Fiction", "Educational", "Comics", "Magazines"],
            "Toys & Games": ["Action Figures", "Board Games", "Puzzles", "Educational Toys", "Video Games"],
            "Health & Beauty": ["Skincare", "Makeup", "Hair Care", "Vitamins", "Fitness Supplements"],
            "Food & Beverages": ["Snacks", "Beverages", "Organic", "Gourmet", "International"]
        }
        
        for parent, subs in subcategories.items():
            for sub in subs:
                cursor.execute("""
                    INSERT INTO categories (name, description, parent_id)
                    VALUES (%s, %s, %s)
                    RETURNING category_id
                """, (sub, f"{sub} in {parent}", category_ids[parent]))
                category_ids[sub] = cursor.fetchone()['category_id']
        
        print(f"   ✓ Created {len(category_ids)} categories")
        
        # ====================================================================
        # 2. SEED USERS
        # ====================================================================
        print("👥 Seeding Users...")
        
        user_ids = []
        
        # Create admin user
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, hashed_password, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """, ("Admin", "User", "admin@ecommerce.com", hash_password("admin123"), "admin"))
        user_ids.append(cursor.fetchone()['user_id'])
        
        # Create regular customers
        for _ in range(50):
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, hashed_password, role)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id
            """, (
                fake.first_name(),
                fake.last_name(),
                fake.unique.email(),
                hash_password("password123"),
                "customer"
            ))
            user_ids.append(cursor.fetchone()['user_id'])
        
        print(f"   ✓ Created {len(user_ids)} users (1 admin, {len(user_ids)-1} customers)")
        
        # ====================================================================
        # 3. SEED ADDRESSES
        # ====================================================================
        print("🏠 Seeding Addresses...")
        
        address_count = 0
        user_addresses = {}
        
        for user_id in user_ids:
            # Each user gets 1-3 addresses
            num_addresses = random.randint(1, 3)
            user_addresses[user_id] = []
            
            for i in range(num_addresses):
                address_type = 'shipping' if i == 0 else random.choice(['shipping', 'billing'])
                cursor.execute("""
                    INSERT INTO addresses (user_id, street, city, zip_code, country, address_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING address_id
                """, (
                    user_id,
                    fake.street_address(),
                    fake.city(),
                    fake.postcode(),
                    fake.country(),
                    address_type
                ))
                address_id = cursor.fetchone()['address_id']
                user_addresses[user_id].append(address_id)
                address_count += 1
                
                # Set first address as default
                if i == 0:
                    cursor.execute("""
                        UPDATE users SET default_address_id = %s WHERE user_id = %s
                    """, (address_id, user_id))
        
        print(f"   ✓ Created {address_count} addresses")
        
        # ====================================================================
        # 4. SEED PRODUCTS
        # ====================================================================
        print("📦 Seeding Products...")
        
        product_ids = []
        
        # Product templates by category
        product_templates = {
            "Smartphones": ["iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus", "Xiaomi"],
            "Laptops": ["MacBook", "Dell XPS", "HP Pavilion", "Lenovo ThinkPad", "ASUS ROG"],
            "Men's Wear": ["T-Shirt", "Jeans", "Jacket", "Sweater", "Polo Shirt"],
            "Women's Wear": ["Dress", "Blouse", "Skirt", "Cardigan", "Leggings"],
            "Furniture": ["Sofa", "Dining Table", "Bed Frame", "Bookshelf", "Office Chair"],
            "Fitness": ["Yoga Mat", "Dumbbells", "Resistance Bands", "Treadmill", "Exercise Ball"],
            "Fiction": ["Mystery Novel", "Romance Novel", "Sci-Fi Book", "Fantasy Book", "Thriller"],
            "Skincare": ["Face Cream", "Cleanser", "Serum", "Sunscreen", "Moisturizer"]
        }
        
        for category_name, products in product_templates.items():
            if category_name in category_ids:
                for product_name in products:
                    # Create 2-3 variations of each product
                    for i in range(random.randint(2, 3)):
                        full_name = f"{product_name} {fake.word().title()}" if i > 0 else product_name
                        base_price = round(random.uniform(19.99, 999.99), 2)
                        
                        cursor.execute("""
                            INSERT INTO products (name, description, base_price, vat_rate, category_id, stock_level, is_active)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING product_id
                        """, (
                            full_name,
                            fake.text(max_nb_chars=200),
                            base_price,
                            0.23,  # 23% VAT
                            category_ids[category_name],
                            random.randint(0, 500),
                            random.choice([True, True, True, False])  # 75% active
                        ))
                        product_ids.append(cursor.fetchone()['product_id'])
        
        print(f"   ✓ Created {len(product_ids)} products")
        
        # ====================================================================
        # 5. SEED PRODUCT VARIANTS
        # ====================================================================
        print("🎨 Seeding Product Variants...")
        
        variant_count = 0
        
        # Add variants to 30% of products
        for product_id in random.sample(product_ids, len(product_ids) // 3):
            variant_type = random.choice(['Color', 'Size', 'Material'])
            
            if variant_type == 'Color':
                values = ['Red', 'Blue', 'Black', 'White', 'Green']
            elif variant_type == 'Size':
                values = ['Small', 'Medium', 'Large', 'XL']
            else:
                values = ['Cotton', 'Polyester', 'Leather', 'Metal']
            
            for value in random.sample(values, random.randint(2, 4)):
                cursor.execute("""
                    INSERT INTO product_variants (product_id, variant_name, variant_value, stock_level, additional_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    product_id,
                    variant_type,
                    value,
                    random.randint(0, 100),
                    round(random.uniform(-5.00, 15.00), 2)
                ))
                variant_count += 1
        
        print(f"   ✓ Created {variant_count} product variants")
        
        # ====================================================================
        # 6. SEED COUPONS
        # ====================================================================
        print("🎟️  Seeding Coupons...")
        
        coupon_codes = [
            ("WELCOME10", "percentage", 10, 0),
            ("SAVE20", "percentage", 20, 50),
            ("FLAT50", "fixed", 50, 100),
            ("SUMMER25", "percentage", 25, 75),
            ("FREESHIP", "fixed", 10, 0),
            ("MEGA30", "percentage", 30, 150),
            ("FIRST15", "percentage", 15, 0),
            ("LOYALTY5", "fixed", 5, 0)
        ]
        
        for code, disc_type, disc_value, min_amount in coupon_codes:
            valid_from = datetime.now() - timedelta(days=random.randint(1, 30))
            valid_until = datetime.now() + timedelta(days=random.randint(30, 90))
            
            cursor.execute("""
                INSERT INTO coupons (code, discount_type, discount_value, valid_from, valid_until, min_order_amount, max_usage)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (code, disc_type, disc_value, valid_from, valid_until, min_amount, random.randint(50, 500)))
        
        print(f"   ✓ Created {len(coupon_codes)} coupons")
        
        # ====================================================================
        # 7. SEED CARTS (Active Shopping Carts)
        # ====================================================================
        print("🛒 Seeding Shopping Carts...")
        
        cart_count = 0
        
        # 40% of users have active carts
        for user_id in random.sample(user_ids[1:], len(user_ids) // 3):
            cursor.execute("""
                INSERT INTO carts (user_id)
                VALUES (%s)
                RETURNING cart_id
            """, (user_id,))
            cart_id = cursor.fetchone()['cart_id']
            
            # Add 1-5 items to cart
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                product_id = random.choice(product_ids)
                
                cursor.execute("""
                    INSERT INTO cart_items (cart_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cart_id, product_id, variant_id) DO NOTHING
                """, (cart_id, product_id, random.randint(1, 3)))
            
            cart_count += 1
        
        print(f"   ✓ Created {cart_count} active shopping carts")
        
        # ====================================================================
        # 8. SEED ORDERS & PAYMENTS
        # ====================================================================
        print("📋 Seeding Orders and Payments...")
        
        order_count = 0
        payment_count = 0
        
        # Create orders for 60% of users
        for user_id in random.sample(user_ids[1:], len(user_ids) * 3 // 5):
            # Each user has 1-4 orders
            num_orders = random.randint(1, 4)
            
            for _ in range(num_orders):
                order_date = fake.date_time_between(start_date='-6M', end_date='now')
                status = random.choice(['new', 'processing', 'shipped', 'delivered', 'delivered', 'delivered'])
                
                # Calculate order total
                num_items = random.randint(1, 6)
                total_amount = 0
                order_items_data = []
                
                for _ in range(num_items):
                    product_id = random.choice(product_ids)
                    cursor.execute("SELECT base_price FROM products WHERE product_id = %s", (product_id,))
                    result = cursor.fetchone()
                    if result:
                        unit_price = float(result['base_price'])
                        quantity = random.randint(1, 3)
                        total_amount += unit_price * quantity
                        order_items_data.append((product_id, quantity, unit_price))
                
                # Create payment first
                payment_status = 'paid' if status != 'new' else random.choice(['paid', 'pending'])
                payment_method = random.choice(['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery'])
                
                cursor.execute("""
                    INSERT INTO payments (amount, status, payment_date, transaction_id, payment_method)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING payment_id
                """, (
                    round(total_amount, 2),
                    payment_status,
                    order_date,
                    fake.uuid4(),
                    payment_method
                ))
                payment_id = cursor.fetchone()['payment_id']
                payment_count += 1
                
                # Create order
                shipping_address = random.choice(user_addresses[user_id])
                
                cursor.execute("""
                    INSERT INTO orders (user_id, order_date, status, total_amount, payment_id, shipping_address_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING order_id
                """, (
                    user_id,
                    order_date,
                    status,
                    round(total_amount, 2),
                    payment_id,
                    shipping_address
                ))
                order_id = cursor.fetchone()['order_id']
                
                # Update payment with order_id
                cursor.execute("""
                    UPDATE payments SET order_id = %s WHERE payment_id = %s
                """, (order_id, payment_id))
                
                # Create order items
                for product_id, quantity, unit_price in order_items_data:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                        VALUES (%s, %s, %s, %s)
                    """, (order_id, product_id, quantity, unit_price))
                
                order_count += 1
        
        print(f"   ✓ Created {order_count} orders")
        print(f"   ✓ Created {payment_count} payments")
        
        # ====================================================================
        # 9. SEED REVIEWS
        # ====================================================================
        print("⭐ Seeding Product Reviews...")
        
        review_count = 0
        
        # Add reviews for 30% of products
        for product_id in random.sample(product_ids, len(product_ids) // 3):
            # Each product gets 1-5 reviews
            num_reviews = random.randint(1, 5)
            reviewers = random.sample(user_ids[1:], min(num_reviews, len(user_ids) - 1))
            
            for user_id in reviewers:
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 30, 40])[0]
                
                cursor.execute("""
                    INSERT INTO reviews (product_id, user_id, rating, content, is_approved)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (product_id, user_id) DO NOTHING
                """, (
                    product_id,
                    user_id,
                    rating,
                    fake.text(max_nb_chars=300),
                    random.choice([True, True, True, False])  # 75% approved
                ))
                review_count += 1
        
        print(f"   ✓ Created {review_count} product reviews")
        
        # ====================================================================
        # COMMIT ALL CHANGES
        # ====================================================================
        print("\n💾 Committing all changes...")
        conn.commit()
        
        # ====================================================================
        # SHOW SUMMARY
        # ====================================================================
        print("\n" + "=" * 70)
        print("✅ DATABASE SEEDING COMPLETED!")
        print("=" * 70)
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        print("\n📊 Final Table Counts:")
        print("-" * 70)
        
        for table in cursor.fetchall():
            table_name = table['table_name']
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"   {table_name:30} | {count:>6} rows")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("E-COMMERCE DATABASE SEEDING")
    print("=" * 70)
    
    success = seed_database()
    
    if success:
        print("\n📝 Next steps:")
        print("1. Run check_db_direct.py to verify data")
        print("2. Start building your FastAPI endpoints")
        print("3. Test with realistic data!")
    else:
        print("\n❌ Seeding failed!")
        sys.exit(1)

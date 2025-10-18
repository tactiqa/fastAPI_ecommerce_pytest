#!/usr/bin/env python3
"""
Migration script to drop UUID-based tables and recreate with SERIAL IDs
WARNING: This will delete all data in the e-commerce tables (except todos)
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

def migrate_to_serial():
    """Drop old UUID tables and create new SERIAL-based tables"""
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Missing DATABASE_URL in .env file")
        return False
    
    try:
        print("=" * 60)
        print("MIGRATION: UUID → SERIAL IDs")
        print("=" * 60)
        print("\nWARNING: This will drop existing e-commerce tables!")
        print("The 'todos' table will NOT be affected.")
        print("\nTables to be dropped:")
        print("  - users, addresses, categories, products")
        print("  - product_variants, carts, cart_items")
        print("  - orders, order_items, payments")
        print("  - reviews, coupons, coupon_usage")
        print("\n" + "=" * 60)
        
        # Check for command line argument to skip confirmation
        if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
            print("Auto-confirmed via --confirm flag")
        else:
            response = input("\nDo you want to continue? (yes/no): ")
            
            if response.lower() != 'yes':
                print("Migration cancelled")
                return False
        
        print("\nConnecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("Dropping old tables...")
        
        # Drop tables in correct order (respecting foreign keys)
        drop_tables = [
            "DROP TABLE IF EXISTS coupon_usage CASCADE",
            "DROP TABLE IF EXISTS order_items CASCADE",
            "DROP TABLE IF EXISTS cart_items CASCADE",
            "DROP TABLE IF EXISTS reviews CASCADE",
            "DROP TABLE IF EXISTS orders CASCADE",
            "DROP TABLE IF EXISTS payments CASCADE",
            "DROP TABLE IF EXISTS carts CASCADE",
            "DROP TABLE IF EXISTS product_variants CASCADE",
            "DROP TABLE IF EXISTS products CASCADE",
            "DROP TABLE IF EXISTS categories CASCADE",
            "DROP TABLE IF EXISTS addresses CASCADE",
            "DROP TABLE IF EXISTS users CASCADE",
            "DROP VIEW IF EXISTS v_products_with_category CASCADE",
            "DROP VIEW IF EXISTS v_order_summary CASCADE",
            "DROP TABLE IF EXISTS coupons CASCADE"
        ]
        
        for drop_sql in drop_tables:
            try:
                cursor.execute(drop_sql)
                table_name = drop_sql.split("IF EXISTS")[1].split("CASCADE")[0].strip()
                print(f"   Dropped {table_name}")
            except Exception as e:
                print(f"   {e}")
        
        conn.commit()
        
        print("\nReading new schema file...")
        sql_file_path = os.path.join(os.path.dirname(__file__), 'sql', 'create_ecommerce_schema_v2.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"SQL file not found: {sql_file_path}")
            return False
        
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        print("Creating new tables with SERIAL IDs...")
        
        try:
            cursor.execute(sql_content)
            conn.commit()
            print("New schema created successfully!")
        except Exception as e:
            conn.rollback()
            print(f"Error creating schema: {e}")
            return False
        
        # Verify tables
        print("\nVerifying created tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print(f"\nSuccessfully created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   {table[0]:30} | {count:>5} rows")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("E-COMMERCE SCHEMA MIGRATION")
    print("UUID-based IDs → SERIAL-based IDs")
    print("=" * 60)
    
    success = migrate_to_serial()
    
    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run check_db_direct.py to verify tables")
        print("2. Start building your FastAPI application")
        print("3. The new schema uses SERIAL IDs (auto-increment integers)")
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)
        sys.exit(1)

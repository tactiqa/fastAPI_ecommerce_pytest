#!/usr/bin/env python3
"""Check the actual schema of the Supabase database"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
database_url = os.getenv('DATABASE_URL')

conn = psycopg2.connect(database_url)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get products table columns
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'products' 
    ORDER BY ordinal_position
""")

print("Products table columns:")
print("-" * 50)
for row in cursor.fetchall():
    print(f"{row['column_name']:20} {row['data_type']}")

# Check if there's data
cursor.execute("SELECT COUNT(*) as count FROM products")
count = cursor.fetchone()['count']
print(f"\nTotal products: {count}")

# Get a sample product
if count > 0:
    cursor.execute("SELECT * FROM products LIMIT 1")
    product = cursor.fetchone()
    print("\nSample product:")
    print("-" * 50)
    for key, value in product.items():
        print(f"{key:20} {value}")

conn.close()

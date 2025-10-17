#!/usr/bin/env python3
"""Check the actual schema of all tables in the Supabase database"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("DATABASE_URL not found in .env file")
    exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor(cursor_factory=RealDictCursor)

tables = [
    "categories",
    "products",
    "product_variants",
    "users",
    "addresses",
    "carts",
    "cart_items",
    "payments",
    "orders",
    "order_items",
    "reviews",
    "coupons",
]

for table in tables:
    print(f"\n--- {table} table schema ---")
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table}' 
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    if not columns:
        print(f"Table '{table}' not found.")
        continue

    for row in columns:
        print(f"{row['column_name']:25} {row['data_type']} erzählen")

conn.close()

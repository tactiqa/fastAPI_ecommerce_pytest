#!/usr/bin/env python3
"""
Direct database connection script to list tables and count rows
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

def check_database_direct():
    """Connect directly to Supabase database and list tables with row counts"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for DATABASE_URL first (full connection string)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        print("🔍 Connecting to Supabase database using DATABASE_URL...")
        try:
            conn = psycopg2.connect(database_url)
            print("✅ Connected successfully!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return
    else:
        # Fall back to individual components
        supabase_url = os.getenv('SUPABASE_URL')
        db_password = os.getenv('DB_PASSWORD')
        
        if not supabase_url or not db_password:
            print("❌ Missing database credentials in .env file")
            print("💡 Add either DATABASE_URL or (SUPABASE_URL + DB_PASSWORD)")
            print("\n📝 Get your database password from:")
            print("   Supabase Dashboard > Project Settings > Database > Database password")
            return
        
        # Extract connection details - Use Transaction Pooler
        project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
        db_host = "aws-1-eu-west-3.pooler.supabase.com"
        db_name = 'postgres'
        db_user = f"postgres.{project_id}"
        db_port = 6543
        
        print("🔍 Connecting to Supabase database...")
        print(f"📊 Host: {db_host} (Transaction Pooler)")
        print(f"👤 User: {db_user}")
        
        try:
            # Connect to database
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=db_port
            )
            print("✅ Connected successfully!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("💡 Check your DB_PASSWORD in .env file")
            return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query to get all tables in public schema with row counts
        query = """
        SELECT 
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        
        cursor.execute(query)
        tables = cursor.fetchall()
        
        if not tables:
            print("📭 No tables found in the public schema")
            return
        
        print(f"\n📊 Found {len(tables)} tables in 'public' schema:")
        print("=" * 60)
        
        # Get row counts for each table
        for table in tables:
            table_name = table['table_name']
            schema = table['table_schema']
            
            try:
                # Count rows in the table
                cursor.execute(f'SELECT COUNT(*) as count FROM "{schema}"."{table_name}"')
                count_result = cursor.fetchone()
                row_count = count_result['count']
                
                print(f"📋 {table_name:25} | {row_count:>8,} rows")
                
                # Optional: Get sample data (first 3 rows)
                if row_count > 0:
                    cursor.execute(f'SELECT * FROM "{schema}"."{table_name}" LIMIT 3')
                    sample_rows = cursor.fetchall()
                    if sample_rows:
                        print(f"   🔍 Sample columns: {list(sample_rows[0].keys())}")
                        for i, row in enumerate(sample_rows[:2], 1):
                            print(f"   Row {i}: {dict(row)}")
                        print()
                
            except Exception as e:
                print(f"📋 {table_name:25} | Error: {str(e)[:50]}...")
        
        # Also show all schemas
        cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT LIKE 'pg_%' 
        AND schema_name != 'information_schema'
        ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        
        print(f"\n🏗️  Available schemas ({len(schemas)}):")
        for schema in schemas:
            print(f"   📁 {schema['schema_name']}")
        
    except ImportError:
        print("❌ Missing psycopg2 library")
        print("💡 Install with: pip install psycopg2-binary")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Check your SUPABASE_SERVICE_ROLE_KEY and network connection")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_direct()

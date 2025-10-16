# How to Get Your Database Password

## 🔑 Steps to Get Database Password from Supabase

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project: `rzsdsbdadqufuxfbtymi`

2. **Navigate to Database Settings**
   - Click on **Settings** (⚙️) in the left sidebar
   - Click on **Database**

3. **Find Database Password**
   - Scroll down to the **Connection string** section
   - You'll see the **Transaction pooler** connection string
   - The format will be:
     ```
     postgresql://postgres.rzsdsbdadqufuxfbtymi:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres
     ```

4. **Copy the Password**
   - Click "Show password" or copy the full connection string
   - Extract the password from `[YOUR-PASSWORD]` part

## 📝 Update Your .env File

### Option 1: Use Full DATABASE_URL (Recommended)
Add this to your `.env` file:
```env
DATABASE_URL=postgresql://postgres.rzsdsbdadqufuxfbtymi:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres
```

### Option 2: Use Individual DB_PASSWORD
Add this to your `.env` file:
```env
SUPABASE_URL=https://rzsdsbdadqufuxfbtymi.supabase.co
DB_PASSWORD=your-actual-database-password-here
```

## ⚠️ Important Notes

1. **Database Password ≠ Service Role Key**
   - The database password is different from `SUPABASE_SERVICE_ROLE_KEY`
   - Service role key is for API access
   - Database password is for direct PostgreSQL connection

2. **Connection Types**
   - **Transaction Pooler** (Port 6543) - Recommended for most apps
   - **Session Pooler** (Port 5432) - For long-running connections
   - **Direct Connection** (Port 5432) - May be blocked by network

3. **Security**
   - Never commit `.env` file to version control
   - Keep your database password secure
   - Rotate passwords regularly

## 🧪 Test Your Connection

After adding the password to `.env`, test it:

```bash
source venv/bin/activate
python check_db_direct.py
```

You should see:
```
✅ Connected successfully!
📊 Found X tables in 'public' schema:
```

## 🔧 Troubleshooting

### "Missing database credentials"
- Make sure you added either `DATABASE_URL` or `DB_PASSWORD` to `.env`

### "Password authentication failed"
- Double-check the password from Supabase dashboard
- Make sure there are no extra spaces or characters

### "Connection timeout"
- Check your internet connection
- Verify the pooler host is correct for your region

## 📸 Visual Guide

The connection string in Supabase looks like this:
```
Transaction pooler
postgresql://postgres.rzsdsbdadqufuxfbtymi:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres

host: aws-1-eu-west-3.pooler.supabase.com
port: 6543
database: postgres
user: postgres.rzsdsbdadqufuxfbtymi
password: [YOUR-PASSWORD]
```

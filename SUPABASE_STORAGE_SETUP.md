# Supabase Storage Setup Guide

## Create the Storage Bucket

To store images in Supabase, you need to create a storage bucket:

### Option 1: Using Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Navigate to **Storage** in the left sidebar
3. Click **"New bucket"**
4. Configure the bucket:
   - **Name**: `classification-images`
   - **Public bucket**: ✅ **Enable** (so images are publicly accessible)
5. Click **"Create bucket"**

### Option 2: Using SQL Editor

If you prefer to use SQL, run this in the Supabase SQL Editor:

```sql
-- Create the bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('classification-images', 'classification-images', true)
ON CONFLICT (id) DO NOTHING;
```

## Set Storage Policies (Important!)

⚠️ **This is the critical step to fix the "row-level security policy" error!**

After creating the bucket, you MUST set policies to allow uploads and public access.

### Quick Fix - Run This SQL

Go to **SQL Editor** in Supabase and run this complete script:

```sql
-- First, make sure the bucket exists and is public
INSERT INTO storage.buckets (id, name, public)
VALUES ('classification-images', 'classification-images', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Drop existing policies if any (to avoid conflicts)
DROP POLICY IF EXISTS "Allow public uploads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public access" ON storage.objects;
DROP POLICY IF EXISTS "Allow public updates" ON storage.objects;
DROP POLICY IF EXISTS "Allow public deletes" ON storage.objects;

-- Create policy to allow anyone to upload files
CREATE POLICY "Allow public uploads"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'classification-images');

-- Create policy to allow anyone to view files
CREATE POLICY "Allow public access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'classification-images');

-- Create policy to allow updates (for overwriting files with same name)
CREATE POLICY "Allow public updates"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'classification-images')
WITH CHECK (bucket_id = 'classification-images');

-- Optional: Create policy to allow deletes
CREATE POLICY "Allow public deletes"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'classification-images');
```

### Using Dashboard (Alternative)

1. Go to **Storage** > **classification-images**
2. Click on **Policies** tab
3. Click **"New Policy"**
4. Choose **"Get started quickly"** > **"Allow all"**
5. This will create all necessary policies automatically

## Verify Setup

After creating the bucket and policies, restart your Flask server:

```powershell
python .\backend\app.py
```

When you upload an image through the web interface, you should see:
- ✓ Image uploaded to Supabase Storage: [URL]
- ✓ Prediction saved to database

## Troubleshooting

### ❌ Error: "new row violates row-level security policy" (403 Unauthorized)

**This is the most common error!** It means the storage policies are missing or incorrect.

**Solution:**
1. Go to Supabase Dashboard > **SQL Editor**
2. Copy and paste the complete SQL script from the "Quick Fix" section above
3. Click **Run** to execute it
4. Restart your Flask server: `python .\backend\app.py`
5. Try uploading an image again

**Quick verification:**
- Go to **Storage** > **classification-images** > **Policies**
- You should see 4 policies: INSERT, SELECT, UPDATE, DELETE
- Each should show `public` as the target role

### Error: "Bucket not found"
- Make sure the bucket name in `config.py` matches exactly: `classification-images`
- Verify the bucket exists in Supabase Dashboard > Storage
- Run the SQL script to create it

### Error: "Permission denied" 
- Check that the bucket is marked as **Public**
- Verify all 4 storage policies exist (see "Quick Fix" SQL above)
- Make sure you're using the correct Supabase URL and anon key in `config.py`
- Make sure you've created the storage policies (see above)
- Verify the bucket is set to **Public**

### Images not showing
- Check that the bucket is marked as **Public**
- Verify the `Allow public access` policy exists for SELECT operations

## Configuration

The bucket name is configured in `backend/config.py`:

```python
SUPABASE_BUCKET = "classification-images"
```

If you use a different bucket name, update this value.

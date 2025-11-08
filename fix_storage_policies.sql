-- ============================================
-- FIX: Row-Level Security Policy Error (403)
-- ============================================
-- Run this script in Supabase SQL Editor to fix the
-- "new row violates row-level security policy" error

-- Step 1: Ensure bucket exists and is public
INSERT INTO storage.buckets (id, name, public)
VALUES ('classification-images', 'classification-images', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Step 2: Drop existing policies (if any) to avoid conflicts
DROP POLICY IF EXISTS "Allow public uploads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public access" ON storage.objects;
DROP POLICY IF EXISTS "Allow public updates" ON storage.objects;
DROP POLICY IF EXISTS "Allow public deletes" ON storage.objects;

-- Step 3: Create INSERT policy (allows uploading files)
CREATE POLICY "Allow public uploads"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'classification-images');

-- Step 4: Create SELECT policy (allows viewing files)
CREATE POLICY "Allow public access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'classification-images');

-- Step 5: Create UPDATE policy (allows overwriting files)
CREATE POLICY "Allow public updates"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'classification-images')
WITH CHECK (bucket_id = 'classification-images');

-- Step 6: Create DELETE policy (allows deleting files)
CREATE POLICY "Allow public deletes"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'classification-images');

-- Step 7: Verify the setup
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'objects' AND policyname LIKE '%public%';

-- You should see 4 policies listed above
-- If successful, restart your Flask server and try uploading again!

# Image URL Construction - Architecture

## Overview
Instead of storing full Supabase Storage URLs in the database, we only store the filename and construct the URL dynamically when needed.

## Benefits
- ✅ Cleaner database schema
- ✅ No data duplication
- ✅ Easier to migrate buckets or change storage locations
- ✅ URLs are always up-to-date with current bucket configuration

## Implementation

### Database Schema
```sql
CREATE TABLE classification (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,              -- Only store filename
    predicted_class TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Backend Flow

1. **Upload Image** (`POST /api/predict`)
   ```python
   # Upload to Supabase Storage
   db.upload_image(image_bytes, unique_filename)
   
   # Save only filename to database
   db.save_prediction(unique_filename, predicted_class, confidence)
   
   # Construct URL for response
   image_url = db.get_image_url(unique_filename)
   ```

2. **Get History** (`GET /api/history`)
   ```python
   # Get predictions from database
   predictions = db.get_all_predictions(limit=limit)
   
   # Add image URLs dynamically
   for prediction in predictions:
       prediction['image_url'] = db.get_image_url(prediction['filename'])
   ```

### Supabase Storage URL Format
```
https://[PROJECT].supabase.co/storage/v1/object/public/[BUCKET]/[FILENAME]
```

Example:
```
https://sjfmoxyekzlkmkcrglyx.supabase.co/storage/v1/object/public/classification-images/20251108_143025_robot.jpg
```

### Code Components

#### `supabase_db.py`
- `upload_image()` - Uploads file to Supabase Storage
- `get_image_url()` - Constructs public URL from filename
- `save_prediction()` - Saves only filename (no URL)

#### `app.py`
- `/api/predict` - Uploads image, saves filename, returns constructed URL
- `/api/history` - Retrieves predictions and adds URLs dynamically

## Frontend Usage
The frontend receives the `image_url` in the API response and can display it directly:

```javascript
// In history modal
modalImage.src = prediction.image_url;
```

## Advantages of This Approach
1. **Flexibility**: Easy to change bucket names or storage providers
2. **Consistency**: All URLs use the same base configuration
3. **Simplicity**: No need to migrate URLs if bucket URL changes
4. **Efficiency**: Smaller database records (no long URLs stored)

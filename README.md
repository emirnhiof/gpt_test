# Media Share Website

This is a simple Flask application that lets users upload photos and videos and share them publicly.

Features:
- Apple-like minimalist design
- Upload images or videos from the **You** page
- See all posts on the **Public** page, where you can like and save posts
- View your saved posts under **Favorites**

## Running

```bash
pip install flask werkzeug
python app/app.py
```

The app stores uploads in `app/uploads/` and metadata in `app/posts.json`.

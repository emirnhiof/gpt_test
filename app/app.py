from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['POSTS_FILE'] = os.path.join(os.path.dirname(__file__), 'posts.json')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

# Helper functions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_posts():
    if not os.path.exists(app.config['POSTS_FILE']):
        return []
    with open(app.config['POSTS_FILE'], 'r') as f:
        return json.load(f)


def save_posts(posts):
    with open(app.config['POSTS_FILE'], 'w') as f:
        json.dump(posts, f)


def get_next_id(posts):
    return max([p['id'] for p in posts], default=0) + 1


@app.route('/')
def index():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return redirect(url_for('public'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('public'))
    return render_template('login.html')


@app.route('/you')
def you():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    posts = [p for p in load_posts() if p['uploader'] == username]
    return render_template('you.html', posts=posts, username=username)


@app.route('/public')
def public():
    posts = load_posts()
    return render_template('public.html', posts=posts)


@app.route('/upload', methods=['POST'])
def upload():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        posts = load_posts()
        post_id = get_next_id(posts)
        posts.append({'id': post_id, 'filename': filename, 'uploader': username, 'likes': 0})
        save_posts(posts)
    return redirect(url_for('you'))


@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    posts = load_posts()
    for p in posts:
        if p['id'] == post_id:
            p['likes'] += 1
            break
    save_posts(posts)
    return redirect(request.referrer or url_for('public'))


@app.route('/save/<int:post_id>', methods=['POST'])
def save(post_id):
    saved = session.get('saved', set())
    if isinstance(saved, list):
        saved = set(saved)
    saved.add(post_id)
    session['saved'] = list(saved)
    return redirect(request.referrer or url_for('public'))


@app.route('/favorites')
def favorites():
    saved = session.get('saved', [])
    posts = [p for p in load_posts() if p['id'] in saved]
    return render_template('favorites.html', posts=posts)


@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

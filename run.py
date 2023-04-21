from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_sslify import SSLify

app = Flask(__name__)
app.secret_key = "secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

sslify = SSLify(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    videos = db.relationship('Video', backref='user', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    video_path = db.Column(db.String(100), nullable=False)
    thumbnail_path = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def home():
    videos = Video.query.order_by(Video.date_created.desc()).all()
    if 'username' in session:
        return render_template('home.html', username=session['username'], videos=videos)
    return render_template('home.html', videos=videos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        video = request.files['video']
        thumbnail = request.files['thumbnail']
        video_path = 'static/videos/' + video.filename
        thumbnail_path = 'static/thumbnails/' + thumbnail.filename
        video.save(video_path)
        thumbnail.save(thumbnail_path)
        video = Video(title=title, video_path=video_path, thumbnail_path=thumbnail_path, user=User.query.filter_by(username=session['username']).first())
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('upload.html')

# Run
if __name__ == '__main__':
    context = ('cert.pem', 'key.pem')
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)
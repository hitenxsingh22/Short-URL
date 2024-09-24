from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(6), unique=True, nullable=False)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    link = URL.query.filter_by(short_url=short_url).first()
    if link:
        return generate_short_url()
    return short_url

# Create tables before running the application
with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        # Check if the URL already exists in the database
        existing_url = URL.query.filter_by(original_url=original_url).first()
        if existing_url:
            return render_template('index.html', short_url=existing_url.short_url)
        
        # Generate a new short URL
        short_url = generate_short_url()
        new_url = URL(original_url=original_url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()
        
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    link = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url)

if __name__ == '__main__':
    app.run(debug=True)

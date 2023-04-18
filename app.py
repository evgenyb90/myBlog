from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog1.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id
    
    def upload_picture(self, picture):
        if not picture:
            return
        

        filename = picture.filename
        file_ext = filename.rsplit('.', 1)[1].lower()

        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            return

        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        self.picture = filename

    def delete_picture(self):
        if not self.picture:
            return

        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], self.picture))
        self.picture = None
    

@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        article.delete_picture()
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "error while deleting an article"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']
        
        if 'delete-picture' in request.form:
            article.delete_picture()
            article.picture = None
        elif request.files['picture']:
            article.delete_picture()
            article.upload_picture(request.files['picture'])
        
        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "error while updating an article"
    else:        
        return render_template("post_update.html", article=article)

    
@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        picture = request.files['picture']

        article = Article(title=title, intro=intro, text=text)
        article.upload_picture(picture)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "error while adding an article"
    else:
        return render_template("create-article.html")



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
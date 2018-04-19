from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blog:1234@localhost:8889/blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body
    
    def __repr__(self):
        return '<Blog %r>' % self.title

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'GET':
        if 'id' in request.args:
            blog_id =  request.args.get('id')
            blog = Blog.query.get(blog_id)
            return render_template('posts.html', title=blog.title, body=blog.body)

    posts = Blog.query.all()
    return render_template('blog-list.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_error = ''
        text_error = ''
        blog_title = request.form['title']
        blog_text = request.form['text']

        if blog_title == '':
            title_error = 'Please give your blog a title!'
        if blog_text == '':
            text_error = 'Text body is empty!'
        
        if title_error != '' or text_error != '':
            return render_template('/newpost.html', title_error=title_error, text_error=text_error)

        new_blog = Blog(blog_title, blog_text)
        db.session.add(new_blog)
        db.session.commit()
        blog = Blog.query.filter_by(title=blog_title).first()
        blog_id = str(blog.id)
        return redirect('/blog?id=' + blog_id)

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
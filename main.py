from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    
    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def index():
    owners = User.query.all()
    return render_template('/index.html', owners=owners)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('Username is already taken')
            return redirect('/signup')
        if username == '':
            flash('Username must not be empty')
            return redirect('/signup')
        if len(username) < 3:
            flash('Username must be longer than 3 characters')
            return redirect('/signup')
        if password != verify:
            flash('Password did not match')
            return redirect('/signup')
        if len(password) < 3:
            flash('Password must be longer than 3 characters')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = username
        return redirect("/blog")
    else:
        return render_template('signup.html')

#TODO: FIX LOGOUT

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user.password == password:
            session['username'] = username
            return redirect ("/")
        flash('bad username or password')
        return redirect("/login")

@app.route("/logout", methods=['GET'])
def logout():
    del session['username']
    return redirect("/index")

endpoints_without_login = ['login', 'signup', 'index', 'blog', 'logout']

@app.before_request
def require_login():
    if not ('username' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'GET':
        if 'owner' in request.args:
            blog_id =  request.args.get('owner')
            blog = Blog.query.get(blog_id)
            user = Blog.query.get(blog.owner_id)
            return render_template('posts.html', title=blog.title, body=blog.body)
            
    posts = Blog.query.all()
    return render_template('blog-list.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()

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

        new_blog = Blog(blog_title, blog_text, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog = Blog.query.filter_by(title=blog_title).first()
        blog_id = str(blog.id)
        return redirect('/blog?id=' + blog_id)

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
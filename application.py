from flask import Flask
from flask import render_template, request, redirect, flash, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash
import os
from os.path import join, dirname
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError

from models import db, Post, User

base_dir = os.path.dirname(__file__)

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), './ignore/.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.urandom(24)
app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET")

migrate = Migrate(app, db)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@login_manager.user_loader
def load_user(user_email):
    return User.query.get(user_email)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        pass
    else:
        posts = Post.query.all()
        return render_template("index.html", posts=posts)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("verify"))

# ユーザーパターンと可能な操作
# 1.メール× → 新規登録
# 2.メール○・認証名×・パスワード○ → ログイン
# 3.メール○・認証名○・パスワード× → Googleからのみログイン
# 4.メール○・認証名○・パスワード○ → ログイン
#メールが存在しない場合のみ新規登録可能
#メールとパスワードのペアが存在する場合のみフォームからログイン可能
@app.route("/api/verify_email/<email>", methods=["GET", "POST"])
def verify_email(email):
    user = User.query.get(email)
    if user is None:
        return jsonify({"available_operations": {"login": False, "register": True}})
    else:
        return jsonify({"available_operations": {"login": bool(user.password_hash), "register": False}})


def verified_register(email, username, password):
    user = User(email=email, username=username, password_hash=generate_password_hash(password, method='pbkdf2:sha256'), auth_username="")
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect("/")

def verified_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.verify_password(password):
        login_user(user)
        return redirect("/")
    else:
        return redirect(f"/verify/{email}/invalid_password")

@app.route("/verify", methods=["GET", "POST"])
@app.route("/verify/<email>/<error>", methods=["GET", "POST"])
def verify(email="", error=""):
    if request.method == "POST":
        form_action = request.form.get("action")
        
        # Register
        if form_action == "register":
            return verified_register(email=request.form.get("email"), username=request.form.get("username"), password=request.form.get("password"))
        # Log in
        elif form_action == "login":
            return verified_login(email=request.form.get("email"), password=request.form.get("password"))
        else:
            # 多分ない
            return redirect(url_for("verify"))
    else:
        if error == "invalid_password":
            return render_template("verify.html", show_message="true", message_context="Error : Invalid password", email=email)
        return render_template("verify.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("verify"))


@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri, prompt='select_account')

@app.route('/auth/callback')
def google_auth_callback():
    try:
        token = google.authorize_access_token()
        res = google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
        user_info = res.json()
        gmail = user_info['email']

        user = User.query.filter_by(email=gmail).first()
        if user is None:
            user = User(email=gmail, username=user_info['name'], password_hash="", auth_username=user_info['name'])
            
            db.session.add(user)
            db.session.commit()
        login_user(user)
        return redirect("/")
    except OAuthError as error:
        flash(f'Authentication failed: {error.description}', 'danger')
        return redirect("/login")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")

        post = Post(title=title, body=body)

        db.session.add(post)
        db.session.commit()

        return redirect("/")
    else:
        return render_template("create.html")

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
@login_required
def update(post_id):
    post = Post.query.get(post_id)
    if request.method == "POST":
        post.title = request.form.get("title")
        post.body = request.form.get("body")

        db.session.commit()

        return redirect("/")
    else:
        return render_template("update.html", post=post)

@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete(post_id):
    post = Post.query.get(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
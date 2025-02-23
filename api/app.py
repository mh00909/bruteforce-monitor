from flask import Flask, render_template, redirect, url_for
from api.routes import api_blueprint
from flask_cors import CORS


app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix="/api")
CORS(app)

app.config['SECRET_KEY'] = 'secret_key'

@app.route("/")
def home():
    return redirect(url_for('login_page'))


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

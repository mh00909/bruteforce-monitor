from flask import Flask, render_template
from api.routes import api_blueprint



app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix="/api")

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

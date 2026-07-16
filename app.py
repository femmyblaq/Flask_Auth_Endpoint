from flask import Flask, render_template #type: ignore
from extension import (bcrypt, mail)
from auth.auth import auth_bp

app = Flask(__name__)

bcrypt.init_app(app)
mail.init_app(app)
app.register_blueprint(auth_bp, url_prefix="/api/auth")

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request
from flask_wtf import CSRFProtect
from blueprint.general import app as general
from blueprint.doctor import app as doctor
from blueprint.registrar import app as registrar
from blueprint.medicine import app as medicine
from blueprint.manzor import app as manzor
import config
from extention import db, socketio
from flask_migrate import Migrate
import os

app = Flask(__name__)

# Config
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = config.SECRET_KEY

# Init extensions
csrf = CSRFProtect(app)
db.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")  # مهم برای دسترسی همه کلاینت‌ها

migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(general)
app.register_blueprint(doctor)
app.register_blueprint(registrar)
app.register_blueprint(medicine)
app.register_blueprint(manzor)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST', 'GET'])
@csrf.exempt
def upload():
    print("=== REQUEST ===")
    print("ARGS:", request.args)
    print("HEADERS:", dict(request.headers))
    print("DATA SIZE:", len(request.get_data() or b""))

    filename = request.args.get("filename") or request.headers.get("X-Filename")

    if not filename:
        return "filename missing", 400

    data = request.get_data()

    if not data:
        return "empty file", 400

    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(data)

    return "OK", 200


# Run
if __name__ == "__main__":
    # debug=True برای توسعه، host='0.0.0.0' برای دسترسی شبکه محلی
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

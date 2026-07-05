from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ai.mindee import extract_receipt
from ai.insights import ai_analytics_data, get_ai_insights

from database.db import db
from database.models import *
from database.crud import save_receipt, get_receipts, get_detailed_receipts

from config import DATABASE_URL

import os
import uuid

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)







@app.route("/upload", methods=["POST"])
def upload():

    image = request.files.get("image")
    print(image.filename)
    print(image.mimetype)
    if image is None:
        return jsonify({
            "success": False,
            "message": "No image received."
        }), 400

    if image.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400


    extension = image.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4()}.{extension}"
    image_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))

    try:

        image.save(image_path)

        receipt = extract_receipt(image_path)

        save_receipt(receipt)

        return jsonify({
            "success": True,
            "message": "Receipt processed successfully."
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if os.path.exists(image_path):
            os.remove(image_path)


@app.route("/receipts", methods=["GET"])
def receipts():
    return jsonify(get_receipts())


@app.route("/detailed_receipts", methods=["GET"])
def detailed_receipts():
    return jsonify(get_detailed_receipts())


@app.route("/insights", methods=["GET"])
def insights():

    try:
        analytics = ai_analytics_data()
        result = get_ai_insights(analytics)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

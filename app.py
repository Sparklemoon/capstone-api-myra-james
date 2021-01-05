from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy   
from flask_marshmallow import Marshmallow
from flask_cors import CORS    
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt  

import os



import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get('postgres://jcqydfrmcbswmt:23ea87404df287326384c16d85b8a77b11851715d05589e9253ccd62d0e11eaf@ec2-35-168-77-215.compute-1.amazonaws.com:5432/d338e1d5sd0shc')

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)


Heroku(app)
CORS(app)

cloudinary.config( 
cloud_name = "sparklemoon", 
api_key = os.environ.get('968967498116363'), 
api_secret = os.environ.get('V2nQFNIJ9QlN_ZIAU-wBd96N4hw')
)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False) 
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, image):
        self.image = image

class ImageSchema(ma.Schema):
    class Meta:
        fields = ("id", "image")

image_schema = ImageSchema()
multiple_image_schema = ImageSchema(many=True)


@app.route("/user/add", methods=["POST"])
def create_user():
    if request.content_type != "application/json":
        return "ERROR JSON NEED PEW PEW"

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    existingUser = db.session.query(User).filter(User.username == username).first()
    if existingUser is not None:
        return jsonify("User already exists")

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    record = User(username, password_hash)
    db.session.add(record)
    db.session.commit()

    return jsonify("User added good job")


@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))


@app.route("/user/authentication", methods=["POST"])
def user_authentication():
    if request.content_type != "application/json":
        return "ERROR JSON NEED PEW PEW"

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify("YOU SHALL NOT PASS")

    if bcrypt.check_password_hash(user.password, password) != True:
        return jsonify("YOU SHALL NOT PASS")
    
    return jsonify("SUCCESS")


@app.route("/image/add", methods=["POST"])
def image_photo():
    if request.content_type != "application/json":
        return"Error: must be set as JSON."

    post_data = request.get_json()
    image = post_data.get("image")

    record = Image(image)
    db.session.add(record)
    db.session.commit()

    return jsonify("Image added good job")

@app.route("/image/get", methods=["GET"])
def get_all_images():
    all_images = db.session.query(Image).all()
    return jsonify(multiple_image_schema.dump(all_images))

@app.route("/image/delete/<id>", methods=["DELETE"])
def delete_image_by_id():
    record = db.session.query(Image).filter(Image.id == id).first()

    db.session.delete(record)
    db.session.commit()
    return jsonify("image DELETED byebye")


if __name__ == "__main__":
    app.run(debug=True)


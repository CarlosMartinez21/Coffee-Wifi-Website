from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import random, requests

API_KEY="A8932ASFjskfh8943gadsb45gjkdfl8wo435"

app = Flask(__name__)
Bootstrap(app)
cafe = {}


##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

# Method to change Cafe DB Object to Dictionary
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    response = requests.get(url="http://127.0.0.1:5000/all")
    data = response.json()
    cafes = data['cafes']
    return render_template("index.html", len=len(cafes), data=cafes)


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = []
    for cafe in cafes:
        all_cafes.append(cafe.to_dict())
    return jsonify(cafes=all_cafes)


@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/search")
def search_cafe():
    location = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=location).first()
    if cafe:
        return jsonify(cafe.to_dict())
    else:
        return jsonify(Error={
            "Not Found": "Sorry, we don't have a cafe at that location"
        })


@app.route("/add", methods=["POST"])
def add_new_cafe():
    name = request.form.get('name')
    map_url = request.form.get('map_url')
    img_url = request.form.get('img_url')
    location = request.form.get('location')
    seats = request.form.get('seats')
    has_toilet = bool(request.form.get('has_toilet'))
    has_wifi = bool(request.form.get('has_wifi'))
    has_sockets = bool(request.form.get('has_sockets'))
    can_take_calls = bool(request.form.get('can_take_calls'))
    coffee_price = request.form.get('coffee_price')
    new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats, has_toilet=has_toilet,
                    has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls, coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={
        "success": "Successfully added the new cafe."
    })


@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def edit_cafe(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify({
            "success": "Successfully updated the price."
        })
    else:
        return jsonify(error={
            "Not Found": "Sorry a cafe with that id was not found"
        })


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe and api_key == API_KEY:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify({
            "success": "Deleted the Cafe."
        })
    elif cafe and api_key != API_KEY:
        return jsonify({
            "error": "Sorry, that's not allowed. Make sure you have the correct api_key"
        })
    else:
        return jsonify(error={
            "Not Found": "Sorry a cafe with that id was not found in the database"
        })


if __name__ == '__main__':
    app.run(debug=True)
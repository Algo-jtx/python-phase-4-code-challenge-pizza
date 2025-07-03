# server/app.py

#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurants_data = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants]
        return make_response(jsonify(restaurants_data), 200)

api.add_resource(Restaurants, '/restaurants')


class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        restaurant_data = restaurant.to_dict()
        return make_response(jsonify(restaurant_data), 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

api.add_resource(RestaurantById, '/restaurants/<int:id>')


class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizzas_data = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]
        return make_response(jsonify(pizzas_data), 200)

api.add_resource(Pizzas, '/pizzas')


# POST /restaurant_pizzas
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)

        except ValueError as e:
            db.session.rollback()
            # --- MODIFICATION STARTS HERE ---
            return make_response(jsonify({"errors": ["validation errors"]}), 400) # Changed from [str(e)]
            # --- MODIFICATION ENDS HERE ---
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": ["An error occurred while creating the RestaurantPizza.", str(e)]}), 400)

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
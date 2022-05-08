from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from data import users, offers, orders
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.url_map.strict_slashes = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    age = db.Column(db.Integer)
    email = db.Column(db.String(40))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(20))


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.Text(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(50))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))


def insert_data_users():
    """Функция заполняет таблицу User"""
    new_users = []
    for user in users:
        new_users.append(
            User(
                id=user["id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                age=user["age"],
                email=user["email"],
                role=user["role"],
                phone=user["phone"]
            )
        )
    with db.session.begin():
        db.session.add_all(new_users)


def insert_data_orders():
    """Функция заполняет таблицу Order"""
    new_orders = []
    for order in orders:
        new_orders.append(
            Order(
                id=order["id"],
                name=order["name"],
                description=order["description"],
                start_date=datetime.strptime(order["start_date"], '%m/%d/%Y'),
                end_date=datetime.strptime(order["end_date"], '%m/%d/%Y'),
                address=order["address"],
                price=order["price"],
                customer_id=order["customer_id"],
                executor_id=order["executor_id"]
            )
        )
    with db.session.begin():
        db.session.add_all(new_orders)


def insert_data_offers():
    """Функция заполняет таблицу Offer"""
    new_offers = []
    for offer in offers:
        new_offers.append(
            Offer(
                id=offer["id"],
                order_id=offer["order_id"],
                executor_id=offer["executor_id"]
            )
        )
    with db.session.begin():
        db.session.add_all(new_offers)


def create_table():
    """Функция заполняет таблицы"""
    insert_data_users()
    insert_data_orders()
    insert_data_offers()


def main():
    db.create_all()
    create_table()

    app.run(debug=True)


@app.route("/users", methods=['GET', 'POST'])
def users_index():
    data = []
    if request.method == 'GET':
        for user in User.query.all():
            data.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "age": user.age,
                "email": user.email,
                "role": user.role,
                "phone": user.phone
            })
        return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        new_users = User(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            email=data["email"],
            role=data["role"],
            phone=data["phone"]
        )
        with db.session.begin():
            db.session.add(new_users)

        return "Пользователь добавлен"


@app.route("/users/<int:uid>", methods=['GET', 'PUT', 'DELETE'])
def users_index_id(uid):
    if request.method == 'GET':
        user = User.query.get(uid)
        data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "email": user.email,
            "role": user.role,
            "phone": user.phone
        }
        return jsonify(data)

    elif request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(uid)

        user.id = data["id"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.age = data["age"]
        user.email = data["email"]
        user.role = data["role"]
        user.phone = data["phone"]

        db.session.add(user)
        db.session.commit()

        return "Пользователь обновлен"

    elif request.method == 'DELETE':
        user = User.query.get(uid)

        db.session.delete(user)
        db.session.commit()

        return "Пользователь удален"


@app.route("/orders", methods=['GET', 'POST'])
def orders_index():
    data = []
    if request.method == 'GET':
        for order in Order.query.all():
            customer = User.query.get(order.customer_id).first_name if User.query.get(
                order.customer_id) else order.customer_id
            executor = User.query.get(order.executor_id).first_name if User.query.get(
                order.executor_id) else order.executor_id
            data.append({
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": customer,
                "executor_id": executor
            })
        return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        new_orders = Order(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            start_date=datetime.strptime(data["start_date"], '%m/%d/%Y'),
            end_date=datetime.strptime(data["end_date"], '%m/%d/%Y'),
            address=data["address"],
            price=data["price"],
            customer_id=data["customer_id"],
            executor_id=data["executor_id"]
        )
        with db.session.begin():
            db.session.add(new_orders)

        return "Пользователь добавлен"


@app.route("/orders/<int:oid>", methods=['GET', 'PUT', 'DELETE'])
def orders_index_id(oid):
    if request.method == 'GET':
        order = Order.query.get(oid)
        customer = User.query.get(order.customer_id).first_name if User.query.get(
            order.customer_id) else order.customer_id
        executor = User.query.get(order.executor_id).first_name if User.query.get(
            order.executor_id) else order.executor_id
        data = {
            "id": order.id,
            "name": order.name,
            "description": order.description,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "address": order.address,
            "price": order.price,
            "customer_id": customer,
            "executor_id": executor
        }
        return jsonify(data)

    elif request.method == 'PUT':
        data = request.get_json()
        order = Order.query.get(oid)

        order.id = data["id"]
        order.name = data["name"]
        order.description = data["description"]
        order.start_date = datetime.strptime(data["start_date"], '%m/%d/%Y')
        order.end_date = datetime.strptime(data["end_date"], '%m/%d/%Y')
        order.address = data["address"]
        order.price = data["price"]
        order.customer_id = data["customer_id"]
        order.executor_id = data["executor_id"]

        db.session.add(order)
        db.session.commit()

        return "Пользователь обновлен"

    elif request.method == 'DELETE':
        order = Order.query.get(oid)

        db.session.delete(order)
        db.session.commit()

        return "Пользователь удален"


@app.route("/offers", methods=['GET', 'POST'])
def offers_index():
    data = []
    if request.method == 'GET':
        for offer in Offer.query.all():
            # customer = User.query.get(order.customer_id).first_name if User.query.get(
            #     order.customer_id) else order.customer_id
            executor = User.query.get(offer.executor_id).first_name if User.query.get(
                offer.executor_id) else offer.executor_id
            data.append({
                "id": offer.id,
                "order_id": offer.id,
                "executor_id": executor
            })
        return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        new_offers = Offer(
            id=data["id"],
            order_id=data["order_id"],
            executor_id=data["executor_id"]
        )
        with db.session.begin():
            db.session.add(new_offers)

        return "Пользователь добавлен"


@app.route("/offers/<int:oid>", methods=['GET', 'PUT', 'DELETE'])
def offers_index_id(oid):
    if request.method == 'GET':
        offer = Offer.query.get(oid)

        data = {
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id
        }
        return jsonify(data)

    elif request.method == 'PUT':
        data = request.get_json()
        offer = Offer.query.get(oid)

        offer.id = data["id"]
        offer.order_id = data["order_id"]
        offer.executor_id = data["executor_id"]

        db.session.add(offer)
        db.session.commit()

        return "Пользователь обновлен"

    elif request.method == 'DELETE':
        offer = Offer.query.get(oid)

        db.session.delete(offer)
        db.session.commit()

        return "Пользователь удален"


if __name__ == "__main__":
    main()

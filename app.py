from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from flask import request, jsonify
import datetime

# initialize app variables
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:Czmpdrdv123!@localhost/e_commerce_api"
)
ma = Marshmallow(app)
db = SQLAlchemy(app)


# initialize customer schemas
# customer schema
class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")


# product schema
class ProductSchema(ma.Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)

    class Meta:
        fields = ("name", "price")


# customer account schema
class CustomerAccount(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=False)

    class Meta:
        fields = ("username", "password", "customer_id")


# customer account schema
class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=True)
    customer = fields.Nested(CustomerSchema)

    class Meta:
        fields = ("username", "password", "customer_id", "customer")


# order schema
class OrderSchema(ma.Schema):
    customer_id = fields.Integer(required=True)
    product_ids = fields.List(fields.Integer(), required=True)

    class Meta:
        fields = ("customer_id", "product_ids")


# initilize schema variables
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
account_schema = CustomerAccount()
accounts_schema = CustomerAccount(many=True)
order_schema = OrderSchema()


# customer table
class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship("Order", backref="customer")


# product table
class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship(
        "Order", secondary="Order_Product", backref="products_in_order"
    )


# order table
class Order(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    products = db.relationship(
        "Product", secondary="Order_Product", backref="orders_in_product"
    )


# customer account table
class CustomerAccount(db.Model):
    __tablename__ = "Customer_Accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    customer = db.relationship("Customer", backref="customer_account", uselist=False)


# order product table
order_product = db.Table(
    "Order_Product",
    db.Column("order_id", db.Integer, db.ForeignKey("Orders.id"), primary_key=True),
    db.Column("product_id", db.Integer, db.ForeignKey("Products.id"), primary_key=True),
)

# initilize database
with app.app_context():
    db.create_all()


# add customer
@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": f"{e}"}), 400

    new_customer = Customer(
        name=customer_data["name"],
        email=customer_data["email"],
        phone=customer_data["phone"],
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "user added"}), 201


# get customer
@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)


# update customer
@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e}), 400
    customer = Customer.query.get_or_404(id)
    customer.name = customer_data["name"]
    customer.email = customer_data["email"]
    customer.phone = customer_data["phone"]
    db.session.commit()
    return jsonify({"Message": "user updated"})


# delete customer
@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "customer deleted"}), 200


# add customer account
@app.route("/customeraccounts", methods=["POST"])
def add_customer_account():
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e})

    new_account = CustomerAccount(
        username=account_data["username"],
        password=account_data["password"],
        customer_id=account_data["customer_id"],
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "customer account created"}), 201


# get customer account
@app.route("/customeraccounts/<int:id>", methods=["GET"])
def get_customer_account(id):
    try:
        customer_account = CustomerAccount.query.filter_by(customer_id=id).first()
    except Exception as e:
        return jsonify({"Error": e}), 404
    result = CustomerAccountSchema().dump(customer_account)
    return jsonify(result), 200


# update customer account
@app.route("/customeraccounts/<int:id>", methods=["PUT"])
def update_customer_account(id):
    try:
        customer_account = CustomerAccount.query.filter_by(
            customer_id=id
        ).first_or_404()
        customer_data = account_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": e}), 400
    customer_account.username = customer_data["username"]
    customer_account.password = customer_data["password"]
    db.session.commit()
    return jsonify({"message": "account updated"}), 200


# delete account
@app.route("/customeraccounts/<int:id>", methods=["DELETE"])
def delete_account(id):
    customer_account = CustomerAccount.query.filter_by(customer_id=id).first_or_404()
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message": "account deleted"}), 200


# add product
@app.route("/products", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e})

    new_product = Product(name=product_data["name"], price=product_data["price"])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"messages": "product added"})


# get products
@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)


# get product
@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.filter_by(id=id).first_or_404()
    return product_schema.jsonify(product)


# update product
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.filter_by(id=id).first_or_404()
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e}), 400

    product.name = product_data["name"]
    product.price = product_data["price"]
    db.session.commit()
    return jsonify({"message": "user updated"})


# delete product
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.filter_by(id=id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "product deleted"}), 200


# add order
@app.route("/orders", methods=["POST"])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e})

    new_order = Order(customer_id=order_data["customer_id"])
    db.session.add(new_order)
    products = Product.query.filter(Product.id.in_(order_data["product_ids"])).all()
    new_order.products.extend(products)
    db.session.commit()


# get order
@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    order = Order.query.get_or_404(id)
    products = order.products
    return jsonify(
        {"order": order_schema.dump(order), "products": products_schema.dump(products)}
    )

from urllib import response
from flask import Flask, jsonify, request
from .models import Dashboard, User, Product
from api import app, db, bcrypt

# This will store session of user because I  did not use render template

session = {}


@app.route('/login-ajax', methods=['POST'])
def login_ajax():
    if request.method == 'OPTIONS':
        response = app.response_class()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    elif request.method == 'POST':
        print("Hi")
        global fernet
        req_json = request.json
        print(req_json)
        email = req_json['email']
        password = req_json['password']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if bcrypt.check_password_hash(user.password, password):
                session["logged_in"] = True
                session["username"] = user.username
                session["email"] = user.email
                print(session)
                if user.username == "admin":
                    return "admin"
                else:
                    return "user"
        return "No User Found. Try Again!!"


@app.route('/logout-ajax', methods=['POST'])
def logout_user():
    global session
    session = {}

    return 'success'


@app.route('/register-ajax', methods=['POST'])
def register_user():
    global fernet
    req_json = request.json
    print(req_json)
    try:
        username = req_json['username']
        firstname = req_json['fname']
        lastname = req_json['lname']
        email = req_json['email']
        password = req_json['password']
        encrypted_password = bcrypt.generate_password_hash(
            password).decode("utf-8")
        values = User(email=email, username=username, fname=firstname,
                      lname=lastname, password=encrypted_password)
        db.session.add(values)
        db.session.commit()
    except Exception as e:
        return str(e)

    return "success"


@app.route('/get-profile-ajax', methods=['GET'])
def get_profile():
    if session.get("email") is not None:
        email = session.get("email")
        print("Email: ", email)
        user = User.query.filter_by(email=email).first()

        response = jsonify({'name': user.fname + " " + user.lname,
                           "email": session['email'], "username": session['username']})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        return "Failed"


@app.route('/add-product-ajax', methods=['POST'])
def add_product():
    if session.get("email") is not None:
        req_json = request.json
        print(req_json)
        try:
            product_name = req_json['product_name']
            category_name = req_json['category_name']
            quantity = req_json['quantity']
            if int(quantity) < 1:
                return "quantity_error"
            product_data = Product.query.filter_by(
                product_name=product_name).first()
            if product_data is not None:
                product_data.quantity += int(quantity)
                db.session.commit()
                return "updated"
            else:
                values = Product(product_name=product_name,
                                 category_name=category_name, quantity=quantity)
                db.session.add(values)
                db.session.commit()
                return "success"
        except Exception as e:
            return str(e)
    else:
        return "Failed"


@app.route('/get-products-ajax', methods=['GET'])
def get_products():
    if session.get("email") is not None:
        products = Product.query.all()
        product_list = []
        for p in products:
            try:
                statuses = Dashboard.query.filter_by(id=p.id).first()
                status = statuses.status
            except:
                status = "Request"
            product_list.append(
                [p.product_name, p.category_name, p.quantity, status, p.id])
        print(product_list)
        response = jsonify(product_list)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        Temp = jsonify("Failed")
        Temp.headers.add('Access-Control-Allow-Origin', '*')
        return Temp


@app.route('/get-requested-products-ajax', methods=['GET'])
def get_req_products():
    try:
        products = Dashboard.query.filter_by(email=session['email'])
        product_list = []
        for p in products:
            product_list.append([p.product_name, p.category_name, p.status])
        print(product_list)

        response = jsonify(product_list)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return str(e)


@app.route('/get-admin-dashboard-ajax', methods=['GET'])
def get_admin_dashboard():
    datas = Dashboard.query.all()
    data_list = []
    for d in datas:
        data_list.append([d.id, d.product_id, d.email,
                         d.product_name, d.category_name, d.status])
    print(data_list)
    user = len(User.query.all())
    products = len(Product.query.all())
    issued_products = Dashboard.query.filter_by(status="Approved").count()
    requested_products = Dashboard.query.filter_by(status="Requested").count()

    response = jsonify({"data_list": data_list, "username": session['username'], "total_user": user,
                       "total_products": products, "total_issued_products": issued_products, "requested_products": requested_products})
    print({"data_list": data_list, "username": session['username'], "total_user": user, "total_products": products,
          "total_issued_products": issued_products, "requested_products": requested_products})

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/status-change-ajax', methods=['POST'])
def status_change():
    req_json = request.json
    print(req_json)
    email = session['email']
    id = req_json['product_id']
    product = Product.query.filter_by(id=id).first()
    product_name = product.product_name
    product_category = product.category_name

    values = Dashboard(id=id, email=email, product_name=product_name,
                       category_name=product_category, status="Requested")
    db.session.add(values)
    db.session.commit()

    return "success"


@app.route('/request-product-ajax', methods=['POST'])
def request_product():
    req_json = request.json
    print("Request ID", req_json)
    email = session['email']
    id = req_json['product_id']
    product = Product.query.filter_by(id=id).first()
    product_name = product.product_name
    product_category = product.category_name

    values = Dashboard(product_id=id, email=email, product_name=product_name,
                       category_name=product_category, status="Requested")
    db.session.add(values)
    db.session.commit()

    return "success"


@app.route('/approve-products-ajax', methods=['POST'])
def approve_products():
    req_json = request.json
    id = req_json['dashboard_id']
    print("This was Dashboard ID", id)
    dashboard_product = Dashboard.query.filter_by(id=id).first()
    ProductId = dashboard_product.product_id
    print("Product ID", ProductId)
    product = Product.query.filter_by(id=ProductId).first()
    temp = product.quantity
    print("product_quantity: ", product.quantity)
    product.quantity = temp - 1
    print("product_quantity: ", product.quantity)
    dashboard_product.status = "Approved"
    db.session.commit()

    return "success"


@app.route('/delete-product-ajax', methods=['POST'])
def delete_product():
    req_json = request.json
    print(req_json)
    id = req_json['product_id']

    # only delete from product table
    product = Product.query.filter_by(id=id).first()

    if product != None:
        db.session.delete(product)
    db.session.commit()

    return "success"

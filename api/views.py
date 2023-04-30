from urllib import response
from flask import Flask, jsonify, request
from .models import Dashboard, User, Product
from api import app, db, bcrypt

# This will store session of user because I  did not use render template

session= {}

@app.route('/login-ajax', methods=['POST'])
def login_user():
    global fernet
    req_json = request.json
    print(req_json)
    email = req_json['email']
    password = req_json['password']
    user= User.query.filter_by(email=email).first()
    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            session["logged_in"] = True
            session["username"]= user.username
            session["email"]=user.email
            print(session)
            if user.username=="admin":
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
        encrypted_password = bcrypt.generate_password_hash(password).decode("utf-8")
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
        print("Email: ",email)
        user= User.query.filter_by(email=email).first()

        response = jsonify({'name': user.fname + " " + user.lname, "email": session['email'], "username":session['username']})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        return "Failed"

@app.route('/get-admin-dashboard-ajax', methods=['GET'])
def get_admin_dashboard():
    datas = Dashboard.query.all()
    data_list = []
    for d in datas:
        data_list.append([d.id, d.product_id, d.email, d.product_name, d.category_name, d.status])
    print(data_list)
    user = len(User.query.all())
    products = len(Product.query.all())
    issued_products = Dashboard.query.filter_by(status="Approved").count()
    requested_products = Dashboard.query.filter_by(status="Requested").count()
    
    response = jsonify({"data_list": data_list,"username":session['username'], "total_user": user, "total_products": products, "total_issued_products": issued_products, "requested_products" :requested_products})
    print({"data_list": data_list,"username":session['username'], "total_user": user, "total_products": products, "total_issued_products": issued_products, "requested_products" :requested_products})

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

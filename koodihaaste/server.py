from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import random

app = Flask(__name__)
client = MongoClient()

dbPlatform = client.platform
messages_col = dbPlatform.messages
customers_col = dbPlatform.customers
users_col = dbPlatform.users


@app.route("/api/messages", methods = ['GET'])
def get_user_messages():
    user_id = request.args.get("user")
    cursor = messages_col.find({"user.id": user_id}, {'_id': False})
    list_cur = list(cursor)
    list_cur.sort(key=lambda x: x["created"], reverse=False)
    return jsonify(list_cur)


@app.route("/api/messages", methods = ['POST'])
def new_message():
    body = request.form['body']
    user = request.form['user']
    customer = request.form['customer']
    cursor = users_col.find({"user": user}, {'_id': False})
    user = list(cursor)[0]

    ct = datetime.datetime.now()
    messages_col.insert_one({
        "user": user,
        "customer": customer,
        "body": body,
        "created": ct

    })

    return "New message uploaded", 202


@app.route("/api/add_customer", methods = ['POST'])
def new_customer():
    customer_name = request.form.get('customer_name')
    contact_person = request.form.get('contact_person')
    if not customer_name:
        return 'Please give customer name', 400
    
    # If contact person not given, give one manually
    if not contact_person:
        cursor = users_col.find()
        list_cur = list(cursor)
        contact_person = list_cur[random.randint(0, (len(list_cur)-1))].get("user")

    ct = datetime.datetime.now()
    customers_col.insert_one({
        "name": customer_name,
        "contact_person": contact_person,
        "created": ct
    })

    return "Customer successfully created", 202


@app.route("/api/add_user", methods = ['POST'])
def new_user():
    user = request.form.get('user')
    email = request.form.get('email')
    if not user:
        return 'Please give user', 400

    if not email:
        return 'Please give email', 400
        
    ct = datetime.datetime.now()
    users_col.insert_one({
        "user": user,
        "email": email
    })
    return "User successfully created", 202


@app.route("/api/update_data", methods = ['PUT'])
def update_data():
    user = request.form.get('user')
    email = request.form.get('email')
    new_user_name = request.form.get('new_user_name')
    new_email = request.form.get('new_email')

    if not user and not email:
        return 'Please give use or email to modify', 400
    
    if user:
        if not new_user_name:
            return 'Please give new username', 400

        cursor = users_col.find({"name": user})
        list_cur = list(cursor)
        if not len(list_cur):
            return f'No user with username "{user}" found', 400
            
        users_col.update_one(
            {"name": user}, 
            {"$set": {"name": new_user_name} })

    if email:
        if not new_email:
            return 'Please give new username', 400

        cursor = users_col.find({"email": email})
        list_cur = list(cursor)
        if not len(list_cur):
            return f'No user with email "{email}" found', 400
            
        users_col.update_one(
            {"email": email}, 
            {"$set": {"email": new_email} })

    return "User successfully updated", 202


if __name__ == "__main__":
    app.run(debug=True)
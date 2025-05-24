from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient
import requests
import math

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo-db:27017/random_users"
app.config["SECRET_KEY"] = "SECRET_KEY"

client = MongoClient(app.config["MONGO_URI"])
db = client.random_users
app.users_collection = db.users

def get_random_users(count):
    try:
        response = requests.get(f"https://randomuser.me/api/?results={count}")
        response.raise_for_status()
        return response.json()["results"]
    except requests.RequestException as e:
        print(f"Error adding users: {str(e)}", flush=True)
        return [], e
    except Exception as e:
        print(f"Error get: {str(e)}", flush=True)
        return [], e

def add_random_users(count):
    users = get_random_users(count)
    if isinstance(users, tuple) and len(users) == 2:
        print(f"No users added, error {users[1]}", flush=True)
        return f"No users added, error 424 {users[1]}", 424
    else:
        try:
            app.users_collection.insert_many(users)
        except Exception as e:
            print(f"Error add: {str(e)}", flush=True)
            return f"Error 500: {str(e)}", 500

@app.route("/")
def index_redirect():
    return redirect(url_for("index"))

@app.route("/homepage", methods=["GET", "POST"])
def index():
    users_per_page = 10
    page = int(request.args.get("page", 1))
    
    if request.method == "POST":
        if "add_num" in request.form:
            add_num = int(request.form.get("add_num", 0))
            if add_num > 0:
                result = add_random_users(add_num)
                if isinstance(result, tuple) and len(result) == 2:
                    return result[0], result[1]
        elif "page_to_go" in request.form:
            try:
                page = int(request.form.get("page_to_go", 1))
                return redirect(url_for("index", page=page))
            except Exception as e:
                print(f"Error page to go: {str(e)}", flush=True)
    try:
        users = app.users_collection.find().skip((page - 1) * users_per_page).limit(users_per_page)
    except Exception as e:
        print(f"Error find: {str(e)}", flush=True)
        return f"Error 500: {str(e)}", 500
    
    try:
        total_users = app.users_collection.count_documents({})
    except Exception as e:
        print(f"Error count: {str(e)}", flush=True)
        return f"Error 500: {str(e)}", 500
    
    total_pages = math.ceil(total_users / users_per_page)
    
    max_pagination_pages = 5
    half_pagination_pages = max_pagination_pages // 2
    start_page = max(1, min(page - half_pagination_pages, total_pages - max_pagination_pages + 1))
    end_page = min(total_pages, start_page + max_pagination_pages - 1)
    pages = range(start_page, end_page + 1)
    
    return render_template("index.html", users=users, page=page, pages=pages, total_pages=total_pages)

@app.route("/homepage/<user_id>")
def user_page(user_id):
    try:
        user = app.users_collection.find_one({"login.uuid": user_id})
        if not user:
            print("User not found", flush=True)
            return "User not found", 404
        page = request.args.get("page", 1)
        return render_template("user.html", user=user, page=page)
    except Exception as e:
        print(f"Error user page: {str(e)}", flush=True)
        return f"Error 500: {str(e)}", 500

@app.route("/homepage/random")
def random_user():
    try:
        user = app.users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
        return render_template("user.html", user=user, page=1)
    except StopIteration:
        print("No users available", flush=True)
        return "No users available", 404
    except Exception as e:
        print(f"Error random: {str(e)}", flush=True)
        return f"Error 500: {str(e)}", 500

if __name__ == "__main__":
    with app.app_context():
        print("Initialization during start server...")
        add_random_users(1000)
    app.run(host="0.0.0.0", port=5000, debug=True)
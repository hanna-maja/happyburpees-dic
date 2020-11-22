import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def get_items():
    items = mongo.db.items.find().sort("name")
    return render_template("dictionary.html", items=items)


@app.route("/sok/")
def search_all_items():
    items = mongo.db.items.find().sort("name")
    return render_template("search-results.html", items=items)


@app.route("/sok/<term>")
def search_items(term):
    items = mongo.db.items.find({"$text": {"$search": term }}).sort("name")
    return render_template("search-results.html", items=items)


@app.route("/ord/<slug>")
def view_item(slug):
    item = mongo.db.items.find_one({"slug": slug})
    return render_template("view-item.html", item=item)


@app.route("/skapa-konto", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        # does username alredy exist in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Användarnamnet finns redan")
            return redirect(url_for("create_account"))

        account = {
            "username": request.form.get("username").lower(),
            "name": request.form.get("name"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(account)

        session["user"] = request.form.get("username").lower()
        flash("Konto skapat")
    return render_template("create-account.html")


@app.route("/logga-in", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # does username alredy exist in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] =  request.form.get("username").lower()
                    flash("Du är inloggad, {}".format(existing_user["name"]))
                    return redirect(url_for("get_items"))
            else:
                # invalid password
                flash("Felaktigt Email eller lösenord")
                return redirect(url_for("login"))
        else:
            # invalid username
            flash("Felaktig Email eller lösenord")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/nytt-ord", methods=["GET", "POST"])
def create_item():
    if request.method == "POST":
         # does item-name alredy exist in db
        existing_item = mongo.db.items.find_one(
            {"name": request.form.get("name")})

        if existing_item:
            flash("Ordet finns redan med i ordlistan")
            return redirect(url_for("create_item"))

        dictionary = {
            "name": request.form.get("name"),
            "short": request.form.get("short"),
            "long": request.form.get("long"),
            "username": session["user"],
            "slug": slugify(request.form.get("name"))
        }
        if request.form.get("href"):
            dictionary["href"] = request.form.get("href")

        mongo.db.items.insert_one(dictionary)

        flash("Nytt ord tillagt")
    return render_template("create-item.html")


@app.route("/min-ordlista")
def my_items():
    items = mongo.db.items.find(
        {"username": session["user"]}
    ).sort("name")
    return render_template("mydictionary.html", items=items)


@app.route("/logga-ut")
def logout():
    flash("Du har blivit utloggad")
    session.clear()
    return redirect(url_for("get_items"))


@app.route("/ta-bort/<id>")
def delete_item(id):
    # delete item from db
    mongo.db.items.remove({"_id": ObjectId(id)})
    flash("Ordet är borttaget")
    return redirect(url_for("my_items"))


@app.route("/redigera/<id>", methods=["GET", "POST"])
def update_item(id):
    if request.method == "POST":
        dictionary = {
            "name": request.form.get("name"),
            "short": request.form.get("short"),
            "long": request.form.get("long"),
            "username": session["user"]
        }
        if request.form.get("href"):
            dictionary["href"] = request.form.get("href")

        mongo.db.items.update({"_id": ObjectId(id)},dictionary)
        flash("Ordet är sparat")
        return redirect(url_for("my_items"))
    item = mongo.db.items.find_one({"_id": ObjectId(id)})
    return render_template("update-item.html", item=item)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

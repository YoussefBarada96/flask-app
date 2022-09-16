import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from werkzeug.utils import secure_filename
import pymongo
from pymongo import MongoClient
client = MongoClient('mongodb+srv://youssef:youssef96@cluster0.2h1xfjv.mongodb.net/?retryWrites=true&w=majority')

db = client["first_app"]
collection = db["users"]

app = Flask(__name__)
app.config.from_object('config')

def read_from_db(collection):
  mydb_list = collection.find({},{'_id':0})
  users_list = []
  pass_list = []
  for x in mydb_list:
    users_list.append(x['username'])
    pass_list.append(x['password'])
  users_list.pop(0)
  pass_list.pop(0)
  return users_list, pass_list

users_list, pass_list = read_from_db(collection)

@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413

@app.route("/")
def FUN_root():
    return render_template("index.html")

@app.route("/public/")
def FUN_public():
    return render_template("public_page.html")

@app.route("/private/")
def FUN_private():
    if "current_user" in session.keys():
        return render_template("private_page.html")
    else:
        return abort(401)

@app.route("/admin/")
def FUN_admin():
    users_list, pass_list = read_from_db(collection)
    if session.get("current_user", None) == "ADMIN":
        user_list = users_list
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("admin.html", users = user_table)
    else:
        return abort(401)

@app.route("/login", methods = ["POST"])
def FUN_login():
    users_list, pass_list = read_from_db(collection)
    id_submitted = request.form.get("id").upper()
    if (id_submitted.lower() in users_list) and request.form.get("pw") in pass_list:
        session['current_user'] = id_submitted
    
    return(redirect(url_for("FUN_root")))

@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return(redirect(url_for("FUN_root")))

@app.route("/delete_user/<id>/", methods = ['GET'])
def FUN_delete_user(id):
    if session.get("current_user", None) == "ADMIN":
        if id == "ADMIN": # ADMIN account can't be deleted.
            return abort(403)
        # [2] Delele the records in database files
        collection.delete_one({'username':id})
        return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)

@app.route("/add_user", methods = ["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN": # only Admin should be able to add user.
        # before we add the user, we need to ensure this is doesn't exsit in database. We also need to ensure the id is valid.
        users_list, pass_list = read_from_db(collection)
        if request.form.get('id').upper() in users_list:
            user_list = users_list
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_duplicated = True, users = user_table))
        if " " in request.form.get('id') or "'" in request.form.get('id'):
            user_list = users_list
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_invalid = True, users = user_table))
        else:
            collection.insert_one({ "username":request.form.get('id'), "password":request.form.get('pw')})
            return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)





if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

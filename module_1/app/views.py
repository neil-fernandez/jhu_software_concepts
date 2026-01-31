from flask import Blueprint, render_template

views = Blueprint("views", __name__)

# Connect URL route '/' to hello() view using decorator
@views.route("/")
def home():
    return render_template("home.html")

@views.route("/contact")
def contact():
    return render_template("contact.html")

@views.route("/projects")
def projects():
   return render_template("projects.html")
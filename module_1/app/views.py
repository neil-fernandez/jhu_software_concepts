"""
This Python script is used to declare three URL routes to web pages
(templates) in a 'views' blueprint.
"""
from flask import Blueprint, render_template

views = Blueprint("views", __name__)    # Create blueprint object

# Connect URL route '/' to home.html view using decorator
@views.route("/")
def home():
    return render_template("home.html")

# Connect URL route '/contact' to contact.html view using decorator
@views.route("/contact")
def contact():
    return render_template("contact.html")

# Connect URL route '/projects' to projects.html view using decorator
@views.route("/projects")
def projects():
   return render_template("projects.html")
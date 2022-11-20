from flask import Blueprint, render_template

HomePage = Blueprint('HomePage', __name__)

@HomePage.route('/')
def home():
    return render_template('home.html')
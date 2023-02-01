from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'angeldust1992'

    from .home import HomePage
    from .search import SearchPage

    app.register_blueprint(HomePage, url_prefix = '/')
    app.register_blueprint(SearchPage, url_prefix='')
   
    return app
from flask import Flask, render_template, Blueprint, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    return 'Hello World'


@app.route('/search', methods=['GET', 'POST'])
def search():
    return 'This is search page'


if __name__ == '__main__':
    app.run()

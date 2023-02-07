from flask import Flask, render_template, Blueprint, request, redirect, url_for

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    return 'Hello World'


@app.route('/search', methods=['GET', 'POST'])
def search():
    form_data = request.form
    print(form_data)
    return redirect('http://localhost:4200/search', code=200)


if __name__ == '__main__':
    app.run(debug=True)

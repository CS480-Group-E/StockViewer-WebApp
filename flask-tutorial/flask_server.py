from flask import Flask, render_template

app = Flask(__name__)


# Landing page
@app.route('/')
def home():
    return 'Welcome to the Home Page!'


# Page 1
@app.route('/page1')
def page1():
    return 'Welcome to Page 1!'


# Page 2
@app.route('/page2')
def page2():
    return 'Welcome to Page 2!'


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask

import backend

app = Flask(__name__)
app.secret_key = 'strawberry'


@app.route('/')
def index():
    return backend.index()


@app.route('/register', methods=['POST', 'GET'])
def register():
    return backend.register()


@app.route('/login', methods=['POST', 'GET'])
def login():
    return backend.login()


@app.route('/logout', methods=['GET'])
def logout():
    return backend.logout()


@app.route('/favorite', methods=['POST', 'GET'])
def favorite():
    return backend.favorite()


@app.route('/fans', methods=['GET'])
def fans():
    return backend.fans()


@app.route('/notification', methods=['GET'])
def notification():
    return backend.notification()


if __name__ == '__main__':
    app.run()

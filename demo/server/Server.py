from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "helloworld"


@app.route('/health')
def health():
    return "ok"


@app.route('/reverse/<string>')
def reverse(string):
    str = string[::-1]
    return str


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
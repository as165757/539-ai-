from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '539 AI API is running!'

from bs4 import BeautifulSoup
import requests
import datetime
import pyautogui
import time
import certifi
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)


# # @app.route('/')
# # def home():
# #     return render_template('testing.html')  ## localhost:5000/  주소 이 상태임.    이게 main 주소.

@app.route('/name')
def sampleLogin():
    return render_template('sample.html')	## localhost:5000/name 이게 메인 주소

##아래부터 추가
@app.route('/main')
def sampleMain():
    return render_template('secondSample.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
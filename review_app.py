from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta16:sparta16@cluster16.b0dkofq.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

import requests
from bs4 import BeautifulSoup



# ----------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/review", methods=["POST"])
def review_post():
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    nickname_receive= request.form['nickname_give']


    doc={
        'star':star_receive,
        'comment':comment_receive,
        'nickname':nickname_receive
    }

    db.review.insert_one(doc)
  
    return jsonify({'msg':'저장 완료!'})


@app.route("/review", methods=["GET"])
def review_get():
    all_reviews = list(db.review.find({},{'_id':False}))
    return jsonify({'result':all_reviews})


@app.route('/review/<string:nickname>', methods=['DELETE']) 
def nickname_del(nickname): 
    db.review.delete_one({'nickname': nickname}) 
    return jsonify({'msg': '삭제완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

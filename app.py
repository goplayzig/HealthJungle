from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import hashlib
import datetime
import jwt
from flask_jwt_extended import *
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.healthyjungle
SECRET_KEY = 'test'

@app.route('/')
def home():
   return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def register():
   id = request.form['id_give']
   pw = request.form['pw_give']
   name = request.form['name_give']

   pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
   db.user.insert_one({'id': id, 'pw': pw_hash, 'name': name})
   return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST'])
def login():
    id = request.form['id_give']
    pw = request.form['pw_give']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id, 'pw': pw_hash})

    if result:
       payload = {
          'id': id,
          'exp': datetime.datetime.now() + datetime.timedelta(seconds=5)   
       }
       token = jwt.encode(payload, SECRET_KEY, algorithm = 'HS256')
       return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)
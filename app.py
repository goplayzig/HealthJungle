from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import hashlib
import datetime
import jwt
from flask_jwt_extended import *
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.healthyjungle
SECRET_KEY = '1g8t4@u%k4@!k9@jh#j0$'

@app.route('/')
def home():
   token_receive = request.cookies.get('myToken')
   print("token_receive", token_receive)
   try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms = ['HS256'])
        print("payload", payload)
        user_info = db.user.find_one({"id": payload['id']})
        print("cookie checked")
      #   return render_template('signUp.html', nickname=user_info["name"])
        return render_template('signUp.html')
   except jwt.ExpiredSignatureError:
      print("cookie expired")
      return render_template('login.html')
      #   return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
   except jwt.exceptions.DecodeError:
      print("cookie undifined")
      return render_template('login.html')
      #   return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/api/signUp', methods=['POST'])
def postSignUp():
    name = request.form['name_give']
    id = request.form['id_give']
    pw = request.form['pw_give']

    user_by_id = db.user.find_one({'id': id})

    if user_by_id:
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 아이디입니다.'})
    
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    db.user.insert_one({'id': id, 'pw': pw_hash, 'name': name})
    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다!'})

@app.route('/api/login', methods=['POST'])
def postLogin():
    id = request.form['id_give']
    pw = request.form['pw_give']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id, 'pw': pw_hash})

    if result:
       payload = {
          'id': id,
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)   
       }
       token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
       print('id, pw', id,pw)
       print('token', token)
       return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
    
@app.route('/signUp')
def signUp():
      return render_template('signUp.html')

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)
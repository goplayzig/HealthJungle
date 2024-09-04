from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from flask.json.provider import JSONProvider
import json
import hashlib
import datetime
import jwt
from flask_jwt_extended import *
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.healthyjungle
SECRET_KEY = '1g8t4@u%k4@!k9@jh#j0$'

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, object):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)

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
        return render_template('calendars.html')
   except jwt.ExpiredSignatureError:
      print("cookie expired")
      return render_template('login.html')
      #   return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
   except jwt.exceptions.DecodeError:
      print("cookie undifned")
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
          'name': result['name'],
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)   
       }
       token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
       return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
    
@app.route('/api/calendar', methods=['POST'])
def postWorkOut():
    token_receive = request.cookies.get('myToken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms = ['HS256'])
        userId = payload['id']
        name = payload['name']
        type = request.form['type_give']
        time = request.form['time_give']
        date = request.form['date']
        memo = request.form['memo_give']
        result = db.workOut.insert_one({'type': type, 'time': time, 'userId': userId, 'date': date, 'memo': memo, 'name': name})
        if result:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'fail', 'msg': '운동 기록에 실패하였습니다.'})
    except jwt.ExpiredSignatureError:
        print("cookie expired")
        return render_template('login.html')
    except jwt.exceptions.DecodeError:
        print("cookie undifned")
        return render_template('login.html')
    
@app.route('/api/calendar', methods=['GET'])
def getWorkOutByDate():
        date = request.args.get('date')
        if date:
            workOut = db.workOut.find({'date': date})
            workOuts = list(workOut)
            print("WWW", workOuts)
            return jsonify({'result': 'success', 'workOuts': workOuts}) 
        else:   
            return jsonify({'result': 'fail', 'message': 'Date parameter is missing'})
    
@app.route('/signUp')
def signUp():
      return render_template('signUp.html')

@app.route('/calendar')
def calendar():
    return render_template('calendars.html')

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)
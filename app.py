from flask import Flask, render_template
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.healthyjungle

@app.route('/')
def home():
   return render_template('login.html')

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)
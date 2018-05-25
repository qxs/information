from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

app = Flask(__name__)

class Config(object):
    DEBUG =True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306:information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

app.config.from_object(Config)

db = SQLAlchemy(app)
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

@app.route("/")
def index():
    redis_store.set('name','wfy')
    return "index"

if __name__ == '__main__':
    app.run()

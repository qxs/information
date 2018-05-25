from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app = Flask(__name__)

class Config(object):
    DEBUG = True
    SECRET_KEY ='ddsfggfgggrffsddddfrfrhhhlsdfklkfoejonnjowwehfwofkwmklfsflnfwo'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306:information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 指定session使用什么来存储
    SESSION_TYPE = 'redis'
    # 指定session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否使用secret_key签名你的sessin
    SESSION_USE_SIGNER = True
    # 设置过期时间，要求'SESSION_PERMANENT', True。而默认就是31天
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24  # 一天有效期
app.config.from_object(Config)

db = SQLAlchemy(app)
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
CSRFProtect(app)
Session(app)
manager = Manager(app)
Migrate(app,db)
manager.add_command('mysql',MigrateCommand)

@app.route("/")
def index():
    from flask import session
    session['age'] = 18
    return "index"

if __name__ == '__main__':
    manager.run()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import configs


db = SQLAlchemy()
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    db = SQLAlchemy(app)
    db.init_app(app)
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)
    CSRFProtect(app)
    Session(app)
    return app
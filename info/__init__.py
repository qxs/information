from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config
from config import Config,ProductionConfig,DevlopmentConfig,UnittestConfig


app = Flask(__name__)
app.config.from_object(ProductionConfig)

db = SQLAlchemy(app)
redis_store = StrictRedis(host=ProductionConfig.REDIS_HOST,port=ProductionConfig.REDIS_PORT)
CSRFProtect(app)
Session(app)
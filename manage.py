from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from config import Config


app = Flask(__name__)
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

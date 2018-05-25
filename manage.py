from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# from info import app,db
from info import create_app,db


app = create_app('dev')
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



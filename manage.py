from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# from info import app, db
from info import create_app, db



# 创建app
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)
# 让迁移和app和数据库建立管理
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command('mysql', MigrateCommand)

from info.modules.index import index_blue
app.register_blueprint(index_blue )

if __name__ == '__main__':

    manager.run()
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# from info import app, db
from info import create_app, db,models  # 这里导入model仅仅为了在迁移时，让ｍａｎａｇｅｒ知道ｍｏｄｅｌｓ的存在
from info.models import User


# 创建app
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)
# 让迁移和app和数据库建立管理
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command('mysql', MigrateCommand)

#创建超级管理员用户脚本
# python manage.py createsuperuser -u sun -m 15555447077 -p 123
@manager.option('-u','-username',dest = 'username')
@manager.option('-m','-mobile',dest = 'mobile')
@manager.option('-p','-password',dest = 'password')
def createsuperuser(username,mobile,password):
    '''创建超级管理员用户的脚本函数'''
    if not all([username,mobile,password]):
        print('缺少必要参数')

    user = User()
    user.nick_name = username
    user.mobile = mobile
    user.password = password
    # is_admin 布尔类型　判断是否是超级管理员用户
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)






if __name__ == '__main__':
    print(app.url_map)
    manager.run()

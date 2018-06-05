from flask import Flask,render_template,g
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_session import Session
# from config import Config, DevlopmentConfig, ProductionConfig, UnittestConfig
from config import configs
import logging
from logging.handlers import RotatingFileHandler




# 创建SQLAlchemy对象
db = SQLAlchemy()
redis_store = None

def setup_log(level):
    """根据创建app时的配置环境，加载日志等级"""
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """创建app的工厂方法
    参数：根据参数选择不同的配置类
    """

    # 根据创建app时的配置环境，加载日志等级
    setup_log(configs[config_name].LEVEL_LOG)

    app = Flask(__name__)

    # 获取配置信息
    app.config.from_object(configs[config_name])

    # 创建连接到MySQL数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    global redis_store
    # 创建连接到redis数据库的对象
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT,decode_responses=True)

    # 开启CSRF保护：因为项目中的表单不再使用FlaskForm来实现，所以不会自动的开启CSRF保护，需要自己开启
    CSRFProtect(app)
    #使用请求钩子，实现数据存储在后端的位置
    @app.after_request
    def setup_csrftoken(response):
        #生成　ｃｓｒｆ＿ｔｏｋｅｎ的值
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token',csrf_token)
        return response

    from info.utils.comment import do_rank
    app.add_template_filter(do_rank,'rank')

    from info.utils.comment import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):
        user = g.user
        context = {
            'user':user.to_dict() if user else None
        }
        return render_template('news/404.html',context=context)


    # 指定session数据存储在后端的位置
    Session(app)

    # 注意点：蓝图再哪里使用，注册就在哪里导入，避免出现蓝图导入过早造成变量不存在的情况
    from info.modules.index import index_blue
    app.register_blueprint(index_blue )
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    from info.modules.user import user_blue
    app.register_blueprint(user_blue)
    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)



    return app
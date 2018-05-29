from . import index_blue
from info import redis_store
from flask import render_template,current_app,session
from info.models import User


@index_blue.route('/')
def index():
    '''登录
    １　处理右上角的登录或者注册显示'''
    user_id = session.get('user_id',None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    context = {
        'user':user
    }

    return render_template('news/index.html',context = context)


@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():
    '''title左侧图标'''
    return  current_app.send_static_file('news/favicon.ico')
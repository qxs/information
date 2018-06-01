#公共的工具文件
from flask import session,current_app,g
from info.models import User
from functools import wraps


def do_rank(index):
    if index==1:
        return 'first'
    elif index==2:
        return 'second'
    elif index==3:
        return 'third'
    else:
        return ''


def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return view_func(*args,**kwargs)
    return wrapper

from flask import Blueprint
from flask import current_app,session,redirect,url_for,request


admin_blue = Blueprint('admin',__name__,url_prefix='/admin')

from . import views


# 使用请求钩子，实现
# l蓝图也可以调用请求钩子
@admin_blue.before_request
def check_admin():
    '''验证用户是否是admin'''
    # １判断是否是管理员，只有管理员才能进入管理的主页，但是管理员必选从后端登录然后去前段．如果从前段登录是不会记录ｓｅｓｓｉｏｎ里的
    # 如果管理员登录了后台，有误入前台界面，会留下私生子（ｉｓ_admin），所以今天谢了这个前代代码，前台用户也能进入后端．
    is_admin = session.get('is_admin', False)
    if not is_admin and not request.url.endswith('/admin/login'):
        return redirect(url_for('index.index'))

# １　如果管理员从前台登录　ｓｅｓｓｉｏｎ不会记录ｉｓ＿ａｄｍｉｎ这条记录，只会记录ｉｄ,nick_name和ｍｏｂｉｌｅ
# 所以上面也是成立的

# ２　　
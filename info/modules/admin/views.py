from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g
from info.models import User
from info.utils.comment import user_login_data
import time,datetime


@admin_blue.route('/user_count')
def user_count():
    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin ==False).count()
    except Exception as e:
        current_app.logger.error(e)

    month_count = 0
    t =time.localtime()
    month_begin = '%d-%02d-01' %(t.tm_year,t.tm_mon)
    month_begin_date = datetime.datetime.strptime(month_begin,'%Y-%m-%d')
    try:
        month_count = User.query.filter(User.is_admin ==False,User.create_time>month_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    day_count = 0
    t = time.localtime()
    day_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon,t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
    context = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count
    }
    return render_template('admin/user_count.html',context=context)



@admin_blue.route('/')
@user_login_data
def admin_index():
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))
    context ={
        'user':user.to_dict()
        # 'user':user.to_dict() if user else None 上面写了　if not user:判断　这里就不用写to_dict() if user else None
    }

    return render_template('admin/index.html',context=context)


@admin_blue.route('/login',methods = ['GET','POST'])
def admin_login():
    if request.method =='GET':
        # 已登录用户访问登录页　直接进入主页面
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username,password]):
            return render_template('admin/login.html',errmsg='缺少参数')
        # ３　查询当前用户是否存在
        try:
            user = User.query.filter(User.nick_name == username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html',errmsg='查询用户名失败')
        if not user:
            return render_template('admin/login.html',errmsg='用户名或者密码错误')

        # 查询密码是否正确
        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或者密码错误')

        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        return redirect(url_for('admin.admin_index'))
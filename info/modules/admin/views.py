from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for
from info.models import User

@admin_blue.route('/')
def admin_index():
    return render_template('admin/index.html')




@admin_blue.route('/login',methods = ['GET','POST'])
def admin_login():
    if request.method =='GET':
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
            return render_template('admin/login.html',errmsg='')
        if not user:
            return render_template('admin/login.html',errmsg='用户名或者密码错误')

        # 查询密码是否正确
        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或者密码错误')

        session['user.id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        return redirect(url_for('admin.admin_index'))
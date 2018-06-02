'''个人中心'''
from . import user_blue
from  flask import render_template,g,current_app,jsonify,url_for,redirect
from info.utils.comment import user_login_data
from info import response_code


@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    # 1 获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user': user
    }

    return render_template('news/user_base_info.html',context=context)


@user_blue.route('/info',methods = ['GET','POST'])
@user_login_data
def user_info():

    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user
    }

    return render_template('news/user.html',context=context)
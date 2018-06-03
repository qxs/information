'''个人中心'''
from . import user_blue
from  flask import render_template,g,current_app,jsonify,url_for,redirect,request,session
from info.utils.comment import user_login_data
from info import response_code,db


@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    # 1 获取登录用户信息

    user = g.user
    if not user:
            return redirect(url_for('index.index'))
    #实现ｇｅｔ请求逻辑
    if request.method == 'GET':
        context = {
            'user': user
        }
        #渲染界面
        return render_template('news/user_base_info.html',context=context)
    #实现ｐｏｓｔ请求逻辑
    if request.method == 'POST':
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        if not all([nick_name,signature,gender]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='保存失败')
        # 注意　：　修改了昵称之后，记得将状态保持中的昵称页修改
        session.nick_name = nick_name

    return jsonify(errno=response_code.RET.OK, errmsg='OK')


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
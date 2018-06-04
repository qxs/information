'''个人中心'''
from . import user_blue
from  flask import render_template,g,current_app,jsonify,url_for,redirect,request,session
from info.utils.comment import user_login_data
from info import response_code,db,constants
from info.utils.file_storage import upload_file



@user_blue.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    if request.method == 'POST':
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        if not all([old_password,new_password]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if not user.check_passowrd(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或者密码错误')

        #　更新密码
        # 调用password属性方法 setter
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='密码保存失败')

        return jsonify(errno=response_code.RET.OK, errmsg='密码保存成功')



@user_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():

    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    if request.method == 'GET':
        context = {
            'user':user.to_dict()
        }

        return render_template('news/user_pic_info.html',context = context)

    if request.method == 'POST':

        avatar_file = request.files.get('avatar')
        #校验参数
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='读取图像失败')

         # 3 上传用户头像
        try:
            key = upload_file(avatar_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传头像失败')

        # ４ 保存用户头像的ｋｅｙ到数据库
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='保存失败')

        data = {
            'avatar_url':constants.QINIU_DOMIN_PREFIX+key
        }

        return jsonify(errno=response_code.RET.OK, errmsg='上传头像成功',data = data)




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
            'user': user.to_dict()
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
        'user':user.to_dict()
    }

    return render_template('news/user.html',context=context)
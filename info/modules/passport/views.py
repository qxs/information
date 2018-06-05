import json,re,random,datetime
from . import passport_blue
from flask import request,abort,current_app,make_response, jsonify,session
from  info.utils.captcha.captcha import captcha
from  info import redis_store,constants,response_code,db
from info.libs.yuntongxun.sms import CCP
from info.models import User


@passport_blue.route('/logout',methods =['GET'])
def logout():
    """退出登录
    清理ｓｅｓｓｉｏｎ　－－－－session.pop('key')
    """
    try:
        session.pop('user_id')
        session.pop('mobile')
        session.pop('nick_name')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='退出登录失败')

    return jsonify(errno=response_code.RET.OK, errmsg='退出登录成功')





@passport_blue.route('/login',methods=['POST'])
def login():
    '''登录
    1 获取参数　校验参数
    ２　查询手机号用户信息　校验用户是否正确　校验密码是否正确  状态保持信息写到ｓｅｓｓｉｏｎ，,完成登录　记录最后一次登录时间
    ３　响应登录结果
    '''
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')
    if not all([mobile,password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号码格式错误')

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e :
        current_app.logger.debug(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户信息错误')
    if not user:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或者密码错误')
    if not user.check_password(password):
        return jsonify(errno=response_code.RET.PWDERR, errmsg='用户名或者密码错误')
    #将状态保持信息写入到ｓｅｓｓｉｏｎ　完成登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    #记录最后一次登录时间
    user.last_login = datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e :
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='记录最后一次登录时间失效')

    return jsonify(errno=response_code.RET.OK, errmsg='登录成功 ')





@passport_blue.route('/resgister',methods=['POST'])
def resgister():
    json_dict = request.json
    mobile = json_dict['mobile']
    smscode_client = json_dict['smscode']
    password = json_dict['password']


    if not all([mobile, smscode_client, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号码格式错误')

    try:
        smscode_server = redis_store.get('SMS:'+mobile)
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询短信验证码失败')
    if not smscode_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='短信验证码不存在')

    if smscode_client != smscode_server:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='输入手机验证码有误')


    user =User()
    user.mobile = mobile
    user.nick_name = mobile
    # #TODO 密码需要加密后再存储
    #方案三：在模型中增加一个属性password，并加载ｓｅｔｔｅｒ和ｇｅｔｔｅｒ方法，调用setter方法直接完成密码的加密和存储
    # setter方法
    user.password = password
    # #记录最后一次登录的时间
    user.last_login = datetime.datetime.now()

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e :
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存注册数据失败')
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    #８响应注册结果
    return jsonify(errno=response_code.RET.OK, errmsg='注册成功')


@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    #"{'mobile':'13829494822','image_code':'asdf','image_code_id':uuid}"
    json_str = request.data.decode('utf-8')
    json_dict = json.loads(json_str)
    mobile = json_dict['mobile']
    image_code_client = json_dict['image_code']
    image_code_id = json_dict['image_code_id']

    if not all([mobile,image_code_client,image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')
    try:
        image_code_server = redis_store.get('imageCoedId:'+image_code_id)
    except Exception as e:
        current_app.logger.erro(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询验证码失败')
    if not image_code_server:
        return jsonify(error=response_code.RET.NODATA,errmsg='图片验证码不存在')

    if image_code_server.lower() != image_code_client.lower():
        return jsonify(error=response_code.RET.PARAMERR, errmsg='输入验证码错误')
    sms_code = '%06d' %random.randint(0,999999)
    current_app.logger.debug(sms_code)
    result = CCP().send_template_sms(mobile,[sms_code,5],1)
    if result != 0:
        return jsonify(error=response_code.RET.THIRDERR, errmsg='发送验证码错误')

    try:
        redis_store.set('SMS:'+mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        return jsonify(error=response_code.RET.DBERR, errmsg='保存验证码失败')

    return jsonify(error=response_code.RET.OK, errmsg='发送验证码成功')



@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    imageCodeId = request.args.get('imageCodeId')
    if not imageCodeId:
        abort(403)

    name,text,image = captcha.generate_captcha()
    current_app.logger.debug(text)
    try:
        redis_store.set('imageCoedId:'+imageCodeId,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logging.error(e)
        abort(500)
    response = make_response(image)
    response.headers['Content-Type']='image/jpg'
    return response


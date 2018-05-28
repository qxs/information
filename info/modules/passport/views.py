import json,re,random
from . import passport_blue
from flask import request,abort,current_app,make_response, jsonify
from  info.utils.captcha.captcha import captcha
from  info import redis_store,constants,response_code
from info.libs.yuntongxun.sms import CCP


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
    try:
        redis_store.set('imageCoedId:'+imageCodeId,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.app.logging.error(e)
        abort(500)
    response = make_response(image)
    response.headers['Content-Type']='image/jpg'
    return response


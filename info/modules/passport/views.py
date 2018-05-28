from . import passport_blue
from flask import request,abort,current_app,make_response
from  info.utils.captcha.captcha import captcha
from  info import redis_store,constants



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


from . import passport_blue
from flask import request

@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    print(request.url)
    # return ''

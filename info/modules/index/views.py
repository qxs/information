from . import index_blue
from info import redis_store
from flask import render_template,current_app


@index_blue.route('/')
def index():
    return render_template('news/index.html')


@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():
    '''title左侧图标'''
    return  current_app.send_static_file('news/favicon.ico')
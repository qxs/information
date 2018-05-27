from . import index_blue
from info import redis_store
from flask import render_template

@index_blue.route('/')
def index():

    return render_template('news/index.html')
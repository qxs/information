from . import index_blue
from info import redis_store
from flask import render_template,current_app,session
from info.models import User,News
from info import constants



@index_blue.route('/')
def index():
    '''登录
    １　处理右上角的登录或者注册显示
    2 新闻点击排行展示，在ｎｅｗｓ数据库中查询，根据点击量ｃｌｉｃｋｓ查询 倒序
    '''

    user_id = session.get('user_id',None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 2 新闻点击排行展示
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    context = {
        'user':user,
        'news_clicks':news_clicks
    }

    return render_template('news/index.html',context = context)


@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():
    '''title左侧图标'''
    return  current_app.send_static_file('news/favicon.ico')
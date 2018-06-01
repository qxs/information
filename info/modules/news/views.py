from . import news_blue
'''新闻详情：收藏,评论，点赞，'''
from flask import render_template,session,current_app,abort,g
from info.models import News,User,constants,Category,db
from info.utils.comment import user_login_data



@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detial(news_id):
    '''1查询用户登录信息
    　　２点击排行
        3新闻查询详情
        4累计点击量'''
    user = g.user

    # 2 新闻点击排行展示
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3 新闻详情查询
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e :
        current_app.logger.error(e)
    if not news:
        abort(404)

    #4累计点击量
    news.clicks +=1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    context = {
        'user': user,
        'news_clicks': news_clicks,
        'news':news.to_dict()
    }

    return render_template('news/detail.html',context = context)
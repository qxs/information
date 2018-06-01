from . import news_blue
'''新闻详情：收藏,评论，点赞，'''
from flask import render_template,session,current_app
from info.models import News,User,constants,Category




@news_blue.route('/detail/<int:news_id>')
def news_detial(news_id):
    '''1查询用户登录信息
    　　２点击排行
        3'''
    user_id = session.get('user_id', None)
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
        'user': user,
        'news_clicks': news_clicks,
        'news':None
    }

    return render_template('news/detail.html',context = context)
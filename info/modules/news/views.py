from . import news_blue
from flask import render_template,session,current_app,abort,g,jsonify,request
from info.models import News,User,constants,Category,db
from info.utils.comment import user_login_data
from info import response_code
'''新闻详情：收藏,评论，点赞，'''

@news_blue.route('/news_collect',methods=['POST'] )
@user_login_data
def news_collect():
    """新闻收藏和取消收藏
        １获取登录用户信息"""
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR,errmsg='用户未登录' )

    news_id = request.json.get('news_id')
    action =request.json.get('action')

    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['collect','cancel_collect']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

    if not news:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    if action == "collect":
        if news not in user.collection_news:
        # 收藏新闻
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            # 取消收藏新闻
            user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')

    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')

@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detial(news_id):
    '''1查询用户登录信息
    　　２点击排行
        3新闻查询详情
        4累计点击量
        5收藏和取消收藏'''

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

    #5收藏和取消收藏/该登录用户收藏了该新闻才显示灰色
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True

    context = {
        'user': user,
        'news_clicks': news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected
    }

    return render_template('news/detail.html',context = context)
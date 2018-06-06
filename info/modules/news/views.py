from . import news_blue
from flask import render_template,session,current_app,abort,g,jsonify,request
from info.models import News,User,constants,Category,db,Comment,CommentLike
from info.utils.comment import user_login_data
from info import response_code
'''新闻详情：收藏,评论，点赞，'''



@news_blue.route('/followed_user',methods=['POST'])
@user_login_data
def followed_user():
    login_user = g.user
    if not login_user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    user_id = request.json.get('user_id')
    action = request.json.get('action')
    if not all([user_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['follow', 'unfollow']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询失败')
    if not other:
        return jsonify(errno=response_code.RET.NODATA, errmsg='用户不存在')

    if action == 'follow':
        if other not in login_user.followed:
            login_user.followed.append(other)
        else:
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='已经关注')
    else:
        if other in login_user.followed:
            login_user.followed.remove(other)
        else:
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='未关注')
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='关注失败')

    return jsonify(errno=response_code.RET.OK, errmsg='关注成功')



'''点赞'''
@news_blue.route('/comment_like',methods=['POST'])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    if not all([comment_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['add','remove']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    #查询点赞的评论是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询失败')
    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg='评论不存在')

    #查询要点赞的评论的赞是否存在，查询当前用户是否给当前的评论点过赞
    try:
        comment_like＿model = CommentLike.query.filter(CommentLike.user_id==user.id,CommentLike.comment_id==comment_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询点赞失败')

    # !!! 点赞和取消点赞－－－－点赞前判断是否没有点赞没有再实现点赞｜｜｜｜｜｜取消点赞前判断是否点了赞　点了赞才能取消点赞
    if action == 'add':
        if not comment_like＿model:
            comment_like＿model = CommentLike()
            comment_like＿model.user_id = user.id
            comment_like＿model.comment_id = comment_id
            db.session.add(comment_like＿model)
            # 累加点赞量
            comment.like_count += 1

    else:
        if comment_like＿model:
            db.session.delete(comment_like＿model)
            # 累减点赞量
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='点赞失败')

    return jsonify(errno=response_code.RET.OK, errmsg='点赞成功')

'''评论'''
@news_blue.route('/news_comment',methods=['POST'])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    if not all([news_id,comment_content]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数' )
    #ajax请求传来的ｎｅｗｓ_id　可能是字符串所以,,没用正则所以可能
    # 校验parent_id 时注意可以有肯恩没有ｐａｒｅｎｔ＿ｉｄ
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='数据库查询失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论失败')

    #注意点：评论完成需要把评论内容渲染出来．　所以return一个　data＝comment.to_dict()　
    return jsonify(errno=response_code.RET.OK, errmsg='OK',data = comment.to_dict())



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
        5收藏和取消收藏
        6 展示死用户评论
        ７关注与取消关注'''

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

    # 6
    # 展示用户评论
    comments = None
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # 7 展示评论点的赞
        # 因为点赞在ｃｏｍｍｅｎｔ　ｄｉｖ里　所以把点赞渲染放在ｃｏｍｍｅｎｔ里面　而收藏只是俩个ａ标签独立的　所以放外面
        # －－－－－－该登录用户给该评论点了赞－－－－－－－

        # 1 查询该登录用户点赞了哪些评论       !!!查出的是一条记录，即对象　每条记录都是一个对象　 |||||下面是错误查询ｇｅｔ需要条件是字段是主键
                                            # comment_id = CommentLike.query.get(user.id)
    comment_like_ids = []
    try:
        comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
    # 2 取出所有被用户点赞的评论 id s
        comment_like_ids = [ comment_like.comment_id for comment_like in comment_likes]
    except Exception as e:
        current_app.logger.error(e)

    #因为我希望界面渲染的数据，是经过处理的，所以我不使用模型原始的数据，而把每个模型类型转换成字典
    # commentｓ这个大的模型对象包括很多comment对象　所以转换成字典
    comment_dict_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 给comment_dict 添加一个 is_like 用于记录该评论是否被该登录用户点赞了
        # 14 ---[21,22]
        # 15 ---[21,22]
        # 21 ---[21,22]
        # 22 ---[21,22]
        comment_dict['is_like'] = False

        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_dict_list.append(comment_dict)

    # ７关注与取消关注
    is_followed = False
    # 用户要登陆且用户看的新闻新闻有作者：
    # user 登录用户　　news,user 作者
    # user.followed 登录用户所关注的人
    if user and News.user:
        if news.user in user.followed:
            is_followed = True

    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected,
        'comments':comment_dict_list,
        'is_followed':is_followed
    }

    return render_template('news/detail.html',context = context)
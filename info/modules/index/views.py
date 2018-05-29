from . import index_blue
from info import redis_store
from flask import render_template,current_app,session,request,jsonify
from info.models import User,News,Category
from info import constants,response_code



@index_blue.route('/news_list')
def index_news_list():
    """提供主页新闻列表数据
    １　接受参数　校验参数（是否是数字）
    ２　根据参数查询用户想看的新闻列表数据
    ３　构造响应的新闻列表数据
    """
    #接受参数　（分类ｉｄ　要看第几页面，每页几条数据）
    cid = request.get('cid',1)
    page = request.get('page',1)
    per_page = request.get('per_page',10)

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    if(cid == 1):
        #最新，时间倒序，每页１０条数据
        paginate = News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
    else:
        paginate = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).painate(page,per_page,False)

    # 4 构造响应的新闻列表数据
        #news_list = [News,News,News,News,News,News,News,News,News,News]   其中News是一个对象
        #取出当前页的所有的模型对象
        news_list = paginate.items
        #读取分页的总数据，将来在主页的新闻列表上拉刷新时使用
        totle_page = paginate.pages
        #读取当前是第几页，将来在主页的新闻列表上拉刷新时使用
        current_page =  paginate.page

        #！！！！！将模型对象字典列表，让json在序列化时可以认识
        news_dict_list = []
        for news in news_list:
            news_dict_list.append(news.to_basic_dict())

        data = {
            'news_dict_list':news_dict_list,
            'totle_page':totle_page,
            'current_page':current_page
        }

    return jsonify(errno=response_code.RET.OK, errmsg='OK',data = data)



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
from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g,abort
from info.models import User,News
from info.utils.comment import user_login_data
import time,datetime
from info import constants



@admin_blue.route('/news_review')
@user_login_data
def news_review():
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))

    page = request.args.get('p','1')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(3)
        page = '1'

    paginate = []
    users = []
    total_page = 1
    current_page =1
    try:
        paginate = News.query.filter(News.status!=0).paginate(page,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        news = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    news_list_dict = []
    for new in news:
        news_list_dict.append(new.to_review_dict())

    context = {
        'news_list':news_list_dict,
        'total_page':total_page,
        'current_page':current_page
    }
    return render_template('admin/news_review.html',context=context)


@admin_blue.route('/user_list')
@user_login_data
def user_list():
    user = g.userK
    if not user:
        return redirect(url_for('admin.admin_login'))

    page = request.args.get('p','1')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(3)
        page = '1'

    paginate = []
    users = []
    total_page = 1
    current_page =1
    try:
        paginate = User.query.filter(User.is_admin==False).paginate(page,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        users = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    user_list_dict = []
    for user in users:
        user_list_dict.append(user.to_admin_dict())

    context = {
        'users':user_list_dict,
        'total_page':total_page,
        'current_page':current_page
    }

    return render_template('admin/user_list.html',context=context)



@admin_blue.route('/user_count')
def user_count():
    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin ==False).count()
    except Exception as e:
        current_app.logger.error(e)

    month_count = 0
    t =time.localtime()
    month_begin = '%d-%02d-01' %(t.tm_year,t.tm_mon)
    month_begin_date = datetime.datetime.strptime(month_begin,'%Y-%m-%d')
    try:
        month_count = User.query.filter(User.is_admin ==False,User.create_time>month_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    day_count = 0
    t = time.localtime()
    day_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon,t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
    context = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count
    }
    return render_template('admin/user_count.html',context=context)



@admin_blue.route('/')
@user_login_data
def admin_index():
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))
    context ={
        'user':user.to_dict()
        # 'user':user.to_dict() if user else None 上面写了　if not user:判断　这里就不用写to_dict() if user else None
    }

    return render_template('admin/index.html',context=context)


@admin_blue.route('/login',methods = ['GET','POST'])
def admin_login():
    if request.method =='GET':
        # 已登录用户访问登录页　直接进入主页面
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username,password]):
            return render_template('admin/login.html',errmsg='缺少参数')
        # ３　查询当前用户是否存在
        try:
            user = User.query.filter(User.nick_name == username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html',errmsg='查询用户名失败')
        if not user:
            return render_template('admin/login.html',errmsg='用户名或者密码错误')

        # 查询密码是否正确
        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或者密码错误')

        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        return redirect(url_for('admin.admin_index'))
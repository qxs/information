from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g,abort,jsonify
from info.models import User,News,Category
from info.utils.comment import user_login_data
import time,datetime
from info import constants,response_code,db
from info.utils.file_storage import upload_file



@admin_blue.route('/news_type',methods=['GET','POST'])
def news_type():
    if request.method == "GET":
        categories = []
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)

        return render_template('admin/news_type.html',categories=categories)

    if request.method == 'POST':
        cname = request.json.get('name')
        cid = request.json.get('id')

        if not cname:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
        #如果有修改分类，否则新增分类
        if cid:
            try:
                cid = int(cid)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数有误")

            try:
                category = Category.query.get(cid)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻分类失败")
            if not category:
                return jsonify(errno=response_code.RET.NODATA, errmsg="分类不存在")

            category.name = cname

        else:
            category = Category()
            category.name = cname
            db.session.add(category)

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻分类失败")

        return jsonify(errno=response_code.RET.OK, errmsg="OK")


@admin_blue.route('/news_edit_detail/<int:news_id>',methods=['GET','POST'])
def news_edit_detail(news_id):

    if request.method=='GET':
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)

        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            abort(404)
        categories.pop(0)

        context = {
            'news': news.to_dict(),
            'categories':categories
        }

        return render_template('admin/news_edit_detail.html',context=context)

    if request.method=="POST":
        # news_id = request.form.get("news_id")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")

        if not all([title, digest, content, category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数有误")

        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻失败")
        if not news:
            return jsonify(errno=response_code.RET.NODATA, errmsg="新闻不存在")

        if index_image:
            try:
                index_image_data = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数有误")
            try:
                key = upload_file(index_image_data)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.THIRDERR, errmsg="图片上传失败")

            # 3. 设置相关数据
        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id

        # 4. 保存到数据库
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg="保存数据失败")
        # 5. 返回结果
        return jsonify(errno=response_code.RET.OK, errmsg="编辑成功")



@admin_blue.route('/news_edit')
def news_edit():
    page = request.args.get('p', '1')
    keyword = request.args.get('keyword')

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(3)
        page = '1'

    paginate = []
    total_page = 1
    current_page = 1
    try:
        if keyword:
            paginate = News.query.filter(News.status ==0, News.title.contains(keyword)).paginate(page,
                                                                                                  constants.ADMIN_USER_PAGE_MAX_COUNT,
                                                                                                  False)
        else:
            paginate = News.query.filter(News.status == 0).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        news = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    news_list_dict = []
    for new in news:
        news_list_dict.append(new.to_basic_dict())

    context = {
        'news_list': news_list_dict,
        'total_page': total_page,
        'current_page': current_page
    }
    return render_template('admin/news_edit.html', context=context)


@admin_blue.route('/news_review_action',methods=['POST'])
def news_review_action():
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['accept','reject']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='新闻查询失败')

    if not news:
            return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

    if action == 'accept':
        news.status = 0
    else:
        news.status =-1
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少原因")
        news.reason = reason
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="通过失败")

    return jsonify(errno=response_code.RET.OK, errmsg='OK')


@admin_blue.route('/news_review_detial/<int:news_id>')
def news_review_detial(news_id):

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not news:
        abort(404)
    context = {
        'news':news
    }

    return render_template('admin/news_review_detail.html',context=context)


@admin_blue.route('/news_review')
def news_review():
    page = request.args.get('p','1')
    keyword = request.args.get('keyword')

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
        if keyword:
            paginate = News.query.filter(News.status != 0,News.title.contains(keyword)).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        else:
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
    # ｙ轴登录量的节点
    active_date = []
    # ｘ轴的时间节点
    active_count = []

    today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    today_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    for i in range(0,15):
        # 计算一天开始
        begin_data = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_data = today_begin_date - datetime.timedelta(days=(i-1))
        # 将ｘ轴对应的开始时间记录
        # strftime:将时间对象转换成时间字符串
        active_date.append(datetime.datetime.strftime(begin_data,'%Y-%m-%d'))

        #查询当天的一户登录量
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_data,User.last_login<end_data).count()
            active_count.append(count)
        except Exception as e:
            current_app.logger.error(e)

    active_count.reverse()
    active_date.reverse()

    context = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count
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
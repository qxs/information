from . import news_blue
'''新闻详情：收藏,评论，点赞，'''
from flask import render_template




@news_blue.route('/detail/<int:news_id>')
def news_detial(news_id):

    return render_template('news/detail.html')
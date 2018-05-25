from redis import StrictRedis


class Config(object):
    DEBUG = True
    SECRET_KEY ='ddsfggfgggrffsddddfrfrhhhlsdfklkfoejonnjowwehfwofkwmklfsflnfwo'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306:information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 指定session使用什么来存储
    SESSION_TYPE = 'redis'
    # 指定session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否使用secret_key签名你的sessin
    SESSION_USE_SIGNER = True
    # 设置过期时间，要求'SESSION_PERMANENT', True。而默认就是31天
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24  # 一天有效期
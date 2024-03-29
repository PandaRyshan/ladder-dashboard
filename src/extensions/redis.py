from redis import Redis
from flask import Flask


@staticmethod
def init(app: Flask) -> Redis:
    return Redis.from_url(app.config['REDIS_URI'])

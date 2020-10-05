import time

from .cache import cache
from .exceptions import TooManyRequests


def extract_unit_and_requests(requests_per_unit):
    # format of requests_per_unit will be like for eg. 1000/h or 10/s or 200/m
    max_requests, unit = requests_per_unit.split("/")
    if unit == "s":
        return max_requests, RateLimitUnit.SECOND
    elif unit == "m":
        return max_requests, RateLimitUnit.MINUTE
    elif unit == "h":
        return max_requests, RateLimitUnit.HOUR
    return max_requests, RateLimitUnit.DAY


class RateLimitUnit:
    SECOND = 1
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 24 * 60 * 60


class RateLimit:
    method = "redis"

    def __init__(self, namespace, resource, max_requests, interval, unit):
        self.namespace = namespace
        self.resource = resource
        self.max_requests = int(max_requests)
        self.unit = unit
        self.interval = self.get_interval(interval)

    def get_key(self, ):
        return "{namespace}:{resource}".format(namespace=self.namespace, resource=self.resource)

    def get_interval(self, interval):
        return interval * self.unit

    def algorithm(self, key, now):
        pipe = cache.pipeline()
        pipe.zremrangebyscore(key, 0, (now - self.interval))
        pipe.zrange(key, 0, -1)
        pipe.zadd(key, {now: now})
        pipe.expire(key, self.interval)
        return pipe.execute()

    def is_throttled(self):
        key = self.get_key()
        now = time.time()
        result = self.algorithm(key, now)
        remaining = max(0, self.max_requests - len(result[1]))
        if remaining > 0:
            print("Message: %s" % ("Allowed to make request, remaining: %s" % remaining))
            return False
        else:
            print("Message: %s" % ("Not Allowed to make request."))
        return True


class RateLimiter:

    def __init__(self, namespace, resource, max_requests, interval, unit=RateLimitUnit.SECOND):
        self.rate_limit = RateLimit(namespace, resource, max_requests, interval, unit)

    def __call__(self, func):
        def inner(*args, **kwargs):
            if self.rate_limit.is_throttled():
                raise TooManyRequests("429 - Too Many Requests")
            return func(*args, **kwargs)

        return inner

    def __enter__(self):
        if self.rate_limit.is_throttled():
            raise TooManyRequests("429 - Too Many Requests")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


rate_limiter = RateLimiter

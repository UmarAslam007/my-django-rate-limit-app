import redis
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
r = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

GROUP_LIMITS = {
    'Gold': 10,
    'Silver': 5,
    'Bronze': 2,
    'Unauthenticated': 1
}

class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = request.META.get('REMOTE_ADDR')
        user = request.user

        if user.is_authenticated:
            group = user.groups.first().name if user.groups.exists() else 'Unauthenticated'
        else:
            group = 'Unauthenticated'

        limit = GROUP_LIMITS.get(group, 1)
        key = f"rate_limit:{ip}"
        count = r.get(key)

        if count is None:
            r.set(key, 1, ex=60)  # expires in 1 minute
        elif int(count) >= limit:
            return JsonResponse({'error': f'{group} user rate limit exceeded'}, status=429)
        else:
            r.incr(key)

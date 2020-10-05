# Python Rate Limiting
Rate Limiting Algorithm implemented using python and redis.

This can be used in two ways, as a function decorator and can be used using with keyword.

In your test.py:

```python
from rest_framework import generics
from throttling import rate_limiter, Rat

class UserAPIView(generics.RetrieveAPIView):
    
    @rate_limiter(namespace="user", resource="post" , interval=1, max_requests=2000, unit=RateLimitUnit.HOUR)
    def create(self, request, *args, **kwargs):
        data = {}
        return Response(data, status=status.HTTP_200_OK)
```
So the above decorator of rate_limiter will limit the requests 2000/hour. Similarily using with keyword - 

```python
from rest_framework import generics
from throttling import rate_limiter, Rat

class UserAPIView(generics.RetrieveAPIView):
    
    def create(self, request, *args, **kwargs):
        with rate_limiter(namespace="user", resource="post" , interval=1, max_requests=2000, unit=RateLimitUnit.HOUR)
            data = {}
            return Response(data, status=status.HTTP_200_OK)
```


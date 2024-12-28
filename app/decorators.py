from functools import wraps
from extensions import cache

def robust_cached(timeout=300):
    """
    A decorator that caches view responses for specified duration.
    Similar to Flask-Caching's @cached but with error handling.
    
    Args:
        timeout (int): Cache timeout in seconds (default: 5 minutes)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                print(f"[Cache] Attempting to fetch/store cache for: {f.__name__} with timeout: {timeout}")
                cached_view = cache.cached(timeout=timeout)(f)
                result = cached_view(*args, **kwargs)
                print(f"[Cache] Cache operation successful for: {f.__name__}")
                return result
            except Exception as e:
                print(f"[Cache] Error in cache operation for {f.__name__}: {str(e)}")
                return f(*args, **kwargs)
        return decorated_function
    return decorator 
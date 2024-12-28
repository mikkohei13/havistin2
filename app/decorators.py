from functools import wraps
from flask_caching import Cache

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
                # Your caching logic here
                return cache.cached(timeout=timeout)(f)(*args, **kwargs)
            except Exception as e:
                # Handle cache errors gracefully
                return f(*args, **kwargs)
        return decorated_function
    return decorator 
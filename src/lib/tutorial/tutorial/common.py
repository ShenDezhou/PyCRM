import functools

rd = redis.Redis()
INDEX_KEY = "index"
def set_cache(key=INDEX_KEY,value):
    rd.set(key,value)

@property
def get_cache(key=INDEX_KEY):
    return rd.get(key)

@property
def incr_cache(key=INDEX_KEY):
    rd.incr(key,1)


def preassert_user(method=None):
    def _assert_usr(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):

            if self.current_user:            
                profile_cache = self.get_cache("user-profile-" + self.current_user)

                if profile_cache:
                    self.current_user_profile = json.loads(profile_cache)

            return method(self, *args, **kwargs)
        return wrapper

    if not method:
        def waiting_for_func(method):
            return _assert_usr(method)
        return waiting_for_func
    else:
        return _assert_usr(method)
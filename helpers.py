
from functools import wraps

def precondition(lambda_func,msg="NBR"):


    def first_wrapper(func):

        @wraps(func)
        def wrapper(*args,**kwargs):


            if lambda_func(*args,**kwargs):
                return func(*args,**kwargs)

            else:
                print(msg)

        return wrapper

    return first_wrapper


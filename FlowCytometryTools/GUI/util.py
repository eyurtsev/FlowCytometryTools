import inspect

def debugging_print(mystr, quiet=True):
    if not quiet:
        print(mystr)


def call_wrapper(func):
    def check_func(*args, **kwargs):
        msg = '-'*20 + '\nFunction: {}\n\t{}\n\t{}\n\t'.format(func.__name__, args, kwargs)
        with open('log.txt','a') as f:
            f.write(msg)
        output = func(*args, **kwargs)
        print msg, '\tReturns {}'.format(output)
        return output

    return check_func


import itertools
def starting_at_five():
     value = raw_input().strip()
     while value != '':
        for el in itertools.islice(value.split(),4,None):
             yield el
        value = raw_input().strip()

def with_head(iterable,headsize=1):
     a , b = itertools.tee(iterable)
     print b.next()
     print b.next()
     print a.next()
     return list(itertools.islice(a,headsize)),b

class User(object):
    def __init__(self,roles):
        print roles
        self.roles = roles

class Unauthorized(Exception):
    pass

def protect(role):
    def _protect(function):
        def _protect(*args,**kw):
            user = globals().get('user')
            print user.roles
            if user is None or role not in user.roles:
                raise Unauthorized("I won't tell you")
            return function(*args,**kw)
        return _protect
    return _protect

class Mysecrets(object):
    @protect('admin')
    def waffle_recipe(self):
        print 'use tons of buffer!'

if __name__ == '__main__':

    '''
    iter = starting_at_five()
    while True:
          print iter.next()
    '''

    '''
    seq = [1,2,3,4,5,6,7]
    print with_head(seq)
    print with_head(seq,4)
    '''

    tarek = User(('admin','user'))
    bill = User(('user',))
    these_are = Mysecrets()
    user = tarek
    these_are.waffle_recipe()
    user = bill
    these_are.waffle_recipe()

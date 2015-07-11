## the choices explicit:
Symbol = str          # A Scheme Symbol is implemented as a Python str
List   = list         # A Scheme List is implemented as a Python list
Number = (int, float) # A Scheme Number is implemented as a Python int or float
Env = dict          # An environment is a mapping of {variable: value}


## Parsing: parse, tokenize and read_from_tokens:

##>>> program = "(begin (define r 10) (* pi (* r r)))"
##>>> tokenize(program)
##result is  a list: ['(', 'begin', '(', 'define', 'r', '10', ')', '(', '*', 'pi', '(', '*', 'r', 'r', ')', ')', ')']
def tokenize(chars):
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token)
        "!!!!!!!!"


## >>> program = "(begin (define r 10) (* pi (* r r)))"
## >>> parse(program)
## result is:['begin', ['define', 'r', 10], ['*', 'pi', ['*', 'r', 'r']]]
def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def parse(program):
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))



## a standard_env
def standard_env():
    "An environment with some Scheme standard procedures."
    import math, operator as op
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.div, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   apply,
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = standard_env()



class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

global_env = standard_env()


##>>> eval(parse("(define r 10)"))
##>>> eval(parse("(* pi (* r r))"))
## get:314.1592653589793

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x                
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)


## use a repl for interaction
##>>> repl()
##lis.py> (define r 10)
##lis.py> (* pi (* r r))
##get: 314.159265359
##lis.py> (if (> (* 11 11) 120) (* 7 6) oops)
##get: 42 
def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(raw_input(prompt)))
        if val is not None: 
            print(schemestr(val))

def schemestr(exp):
    "Convert a Python object back into a Scheme-readable string."
    if  isinstance(exp, list):
        return '(' + ' '.join(map(schemestr, exp)) + ')' 
    else:
        return str(exp)

## define procedures and environments
class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

global_env = standard_env()

## final test
##>>> repl()
##lis.py> (define circle-area (lambda (r) (* pi (* r r))))
##lis.py> (circle-area 3)
##28.274333877

##lis.py> (define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
##lis.py> (fact 10)
##3628800
##lis.py> (fact 100)
##93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000
##lis.py> (circle-area (fact 10))
##4.1369087198e+13


##lis.py> (define first car)
##lis.py> (define rest cdr)
##lis.py> (define count (lambda (item L) (if L (+ (equal? item (first L)) (count item (rest L))) 0)))
##lis.py> (count 0 (list 0 1 2 3 0 0))
##3
##lis.py> (count (quote the) (quote (the more the merrier the bigger the better)))
##4

##lis.py> (define twice (lambda (x) (* 2 x)))
##lis.py> (twice 5)
##10

##lis.py> (define repeat (lambda (f) (lambda (x) (f (f x)))))
##lis.py> ((repeat twice) 10)
##40

##lis.py> ((repeat (repeat twice)) 10)
##160
##lis.py> ((repeat (repeat (repeat twice))) 10)
##2560
##lis.py> ((repeat (repeat (repeat (repeat twice)))) 10)
##655360
##lis.py> (pow 2 16)
##65536.0


##lis.py> (define fib (lambda (n) (if (< n 2) 1 (+ (fib (- n 1)) (fib (- n 2))))))
##lis.py> (define range (lambda (a b) (if (= a b) (quote ()) (cons a (range (+ a 1) b)))))
##lis.py> (range 0 10)
##(0 1 2 3 4 5 6 7 8 9)

##lis.py> (map fib (range 0 10))
##(1 1 2 3 5 8 13 21 34 55)
##lis.py> (map fib (range 0 20))
##(1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987 1597 2584 4181 6765)


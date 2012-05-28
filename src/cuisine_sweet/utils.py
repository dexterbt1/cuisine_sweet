import sys
import inspect
import pexpect
from decorator import decorator
from fabric.api import puts
from fabric.colors import green

def this_func(level=1):
    frm = inspect.stack()[level]
    mod = inspect.getmodule(frm[0])
    return '%s.%s' % (mod.__name__, frm[3])


def completed_ok(arg_output=[]):
    def wrapped_f(func, *args, **kwargs):
        r = func(*args, **kwargs)
        out = []
        for i in arg_output:
            out.append(args[i])
        puts(green('%s.%s(%s): OK' % (func.__module__, func.__name__, ', '.join(out))))
        return r
    return decorator(wrapped_f) # needed to preserve: func signature, docstring, name
        

def local_run_expect(cmd, prompts, answers, logfile=sys.stdout):
    child = pexpect.spawn(
        cmd,
        timeout=1800,
        )
    child.logfile = logfile
    child.delaybeforesend = 0
    while True:
        try:
            i = child.expect(prompts)
            if i <= len(answers)-1:
                child.sendline(answers[i])
        except pexpect.EOF:
            break

"""
Fabric checks and assertions for Supervisord instances
"""

import cuisine
from fabric.api import run, sudo
from cuisine_sweet.utils import completed_ok


@completed_ok(arg_output=[0])
def dir_created(name, **kwargs):
    """
    Ensure that the directory is created and with proper permissions.
    
    Wraps cuisine.dir_ensure function
    """
    cuisine.dir_ensure(name, **kwargs)


@completed_ok(arg_output=[0,1])
def dir_symlink_created(src, dest):
    """
    Ensure that a symlink at `dest` pointing to `src` is created.
    """
    run('ln -s %s %s >& /dev/null; true' % (src, dest))
    run('test -L %s && test -d %s' % (dest, dest))

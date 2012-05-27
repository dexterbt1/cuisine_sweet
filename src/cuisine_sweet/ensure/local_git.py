"""
Fabfile functions for ensuring the state of a local git checkout

This is primarly used for fabfiles that are version-controlled in git. 
"""
    
import cuisine 
from fabric.api import local, abort, puts, lcd
from fabric.colors import green, blue, red
from cuisine_sweet.utils import this_func


def up_to_date(against=None, path='.'):
    """
    Check if the git checkout in ``path`` is up-to-date ``against`` another refspec.

    :param against: *required* str; refspec to check against
    :param path: str; path to the local clone/checkout directory

    This function will ensure that the current checkout where the fabfile is located
    is up to date. 

    It solves the problem of accidentally deploying an old version of the fabfile.
    This is a potential issue in a multiuser setup with many users each having their 
    own checkout, and some forgetting to update their checkouts.

    The common usage is to maintain two checkouts, e.g.:
    
    - checkout1 - this is where you develop your fabfile. From here, push commits to some  central_repo
    - checkout2 - this is where you deploy your fabfile from. It is here that you do ``git fetch + git reset + fab ...``
    """
    if not against:
        abort(red("Missing arg: against"))
    with lcd(path):
        num_changes_str = local('git fetch && git rev-list HEAD..%s | wc -l' % against, capture=True)
        num_changes = int(num_changes_str)
        if num_changes > 0:
            abort(red("%s: Your git checkout at path=%s is not up-to-date against=%s (forgot to pull?)." % (this_func(), path, against)))
        puts(green("%s(against=%s): OK" % (this_func(), against)))


def clean(path='.'):
    """
    Check if the git checkout in ``path`` is free from dirty/uncommitted changes.

    :param path: str; path to the local clone/checkout directory

    For production / stable deploys, this will make sure that you are deploying
    a fabfile that is not tampered / accidentally modified / have untested uncommited feature.
    """
    num_changes_str = local('git status --porcelain | wc -l', capture=True)
    num_changes = int(num_changes_str)
    if num_changes > 0:
        abort(red("%s: Your current checkout has uncommitted changes." % this_func()))
    puts(green("%s: OK" % this_func()))



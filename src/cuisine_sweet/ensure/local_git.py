"""
Fabric checks and assertions for a local git checkout
"""
    
import cuisine 
from fabric.api import local, abort, puts, lcd
from fabric.colors import green, blue, red
from cuisine_sweet.utils import this_func


def up_to_date(against=None, path='.'):
    """
    Check if the git checkout in `path` is up-to-date `against` another refspec.
    
    The param `against` is usually set to 'origin/master'; then this function 
    will only succeed if the checkout has the latest commits from 'origin/master'.
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
    Check if the git checkout in `path` is free from dirty/uncommitted changes.
    """
    num_changes_str = local('git status --porcelain | wc -l', capture=True)
    num_changes = int(num_changes_str)
    if num_changes > 0:
        abort(red("%s: Your current checkout has uncommitted changes." % this_func()))
    puts(green("%s: OK" % this_func()))



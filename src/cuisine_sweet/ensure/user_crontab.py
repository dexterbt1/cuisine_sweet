"""
Fabfile functions for ensuring the state of a user's crontab

A user-crontab is a crontab schedule for a specific user, usually
loaded from a file (for version-control purposes).
"""

from fabric.api import run, sudo
from cuisine_sweet.utils import completed_ok


@completed_ok(arg_output=[0])
def loaded(crontab_file):
    """
    Ensure that the user's crontab file is loaded.

    :param crontab_file: *required* str; path to the crontab file

    This ensures that the correct crontab is loaded. 
    Correct means the loaded one should match what is in the file. 
    Otherwise it gets reloaded from the file.
    """
    run('which md5sum')
    loaded = run('crontab -l >& /dev/null && echo OK; true').endswith('OK')
    if loaded:
        loaded_checksum = run('crontab -l | md5sum')
        expected_checksum = run('cat %s | md5sum' % crontab_file)
        if loaded_checksum != expected_checksum:
            # reload
            run('crontab %s' % crontab_file)
    else:
        run('crontab %s' % crontab_file)


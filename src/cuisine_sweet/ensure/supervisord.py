"""
Fabfile functions for ensuring the state of a supervisord instance

See `Supervisord <http://www.supervisord.org>`_ - an open-source process-control system.
"""

import re
import time
import cuisine
from fabric.api import run, sudo
from cuisine_sweet.utils import completed_ok


@completed_ok()
def installed(version=None):
    """
    Ensure that the supervisord is installed.

    :param version: str; the exact version string to install (e.g. "3.0a12")

    If supervisord is not present, the package is sudo() installed via ``easy_install``.
    
    Currently RHEL/CentOS flavored.
    """
    cuisine.select_package(option='yum') 
    cuisine.command_ensure('easy_install', package='python-setuptools')
    if not cuisine.command_check('supervisord'):
        if version:
            sudo('easy_install supervisor==%s' % version)
        else:
            sudo('easy_install supervisor')
            
        


@completed_ok(arg_output=[0])
def running(configfile, pidfile, basedir=None, envsource=None, sudo=False):
    """
    Ensure that the supervisord instance is running with the correct config.

    :param configfile: *required* str; path to the configfile
    :param pidfile: *required* str; path to the pidfile
    :param basedir: str; the base directory where supervisor will be run
    :param envsource: str; path to the shell-script to load before running supervisord
    :param sudo: bool; run supervisord under sudo(), otherwise via run()

    Instance checking is based whether the process pid read from pidfile 
    is running.

    If basedir is specified, it overrides the '-d' parameter passed when
    running the supervisord daemon. If not specified, then the current
    working directory (via ``pwd``) is used. 

    If envsource is specified, prior to starting the supervisord daemon,
    this path-to-shell-script-environment gets loaded (via ``source``)

    If sudo is true, then the supervisord daemon is started via sudo(),
    otherwise, uses the default run() user.
    """
    if not basedir:
        basedir = run('pwd') # current working directory
    pid = run('cat %s; true' % pidfile)

    running = False
    if re.match(r'^\d+$', pid):
        # check
        pid_running = run('ps -p %s && echo OK; true' % pid).endswith('OK')
        if pid_running:
            # ensure that we are using the correct config, otherwise kill first
            running_cmd = run('ps -p %s ho cmd' % pid)
            running_cfg_match = re.match(r'.*-c\s+(\S+).*', running_cmd)
            do_kill = True
            if running_cfg_match:
                running_cfg = running_cfg_match.group(1)
                if running_cfg == configfile:
                    do_kill = False
                    running = True

            if do_kill:
                # kill impostor or old process
                run('kill %s && sleep 1; true' % pid)

    if not running:
        xcmd = 'supervisord -d %s -c %s -j %s' % (basedir, configfile, pidfile)
        if envsource:
            xcmd = 'source %s && %s' % (envsource, xcmd)
        if sudo:
            sudo(xcmd)
        else:
            run(xcmd)
        time.sleep(3)

    # --- test pid if running
    pid = run('cat %s; true' % pidfile)
    run('kill -0 %s' % pid)



@completed_ok(arg_output=[0])
def updated_with_latest_config(configfile):
    """
    Ensure that the latest config of the supervisord is loaded and reflected.

    :param configfile: *required* str; path to the configfile

    If there are any changes in the supervisord config, the supervisord
    process must be able to do the ff:

    - start newly added programs
    - stop deleted programs
    - restart programs with updated config

    All these is automatically handled via Supervisord's ``reread`` and ``update``
    commands.

    Assumption: The ``configfile`` must contain the correct settings for ``[supervisorctl]``
    including the username and password.
    """
    run('which supervisorctl')
    run('supervisorctl -c %s reread' % configfile)
    run('supervisorctl -c %s update' % configfile)
    run('supervisorctl -c %s restart all' % configfile)


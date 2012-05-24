"""
Fabric checks and assertions for Supervisord instances
"""

import re
import cuisine
from fabric.api import run, sudo
from cuisine_sweet.utils import completed_ok


@completed_ok()
def installed():
    """
    Ensure that the supervisord is installed.
    """
    cuisine.select_package(option='yum')
    cuisine.command_ensure('easy_install', package='python-setuptools')
    if not cuisine.command_check('supervisord'):
        sudo('easy_install supervisor')


@completed_ok(arg_output=[0])
def running(configfile, pidfile, basedir=None, envsource=None, sudo=False):
    """
    Ensure that the supervisord instance is running with the correct config.

    Instance checking is based whether the process pid read from pidfile 
    is running.

    If basedir is specified, it overrides the '-d' parameter passed when
    running the supervisord daemon. If not specified, then the current
    working directory (via `pwd`) is used. 

    If envsource is specified, prior to starting the supervisord daemon,
    this path-to-shell-script-environment gets loaded (via `source`)

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
            


@completed_ok(arg_output=[0])
def updated_with_latest_config(configfile):
    """
    Ensure that the latest config of the supervisord is loaded and reflected.
    """
    run('which supervisorctl')
    run('supervisorctl -c %s reread' % configfile)
    run('supervisorctl -c %s update' % configfile)


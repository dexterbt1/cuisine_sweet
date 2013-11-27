"""
Fabfile functions for ensuring the state of deployed code from git
"""

import os
import sys
import cuisine

from fabric.api import env, cd, lcd, local, run, put, abort
from fabric.utils import error
from fabric.auth import get_password
from fabric.network import normalize

from cuisine_sweet import git
from cuisine_sweet.utils import completed_ok, local_run_expect


@completed_ok(arg_output=[0,1])
def rsync(repo_url, repo_dir, refspec='master', home='.', base_dir='git', local_tmpdir='/tmp', save_history=False, do_delete=True):
    """
    Does a git clone locally first then rsync to remote.

    :param repo_url: *required* str; url of the git repo
    :param repo_dir: *required* str; dir name of the repo clone
    :param refspec: str; the git refspec to checkout for deploy (can be a branch, tag, git hash, etc.)
    :param home: str; home directory to deploy the code to.
    :param base_dir: str; dir name relative to ``home``. 
    :param local_tmpdir: str; where the local clone + checkout will be located
    :param save_history: bool; if True, then the history of every deploys is tracked, for rollback purposes later.
    :param do_delete: bool; if True, then rsync parameter --delete-during will be added

    Problem statement: How do we ensure that code from a git repository gets deployed 
    uniformly, efficiently across all remote hosts.

    This is one solution that uses ``rsync`` to push code (just as fabric is push-based).
    Git returns to being a code/config repository and is not required in the destination hosts.

    Another advantage of this approach is when not all destination hosts have access to the 
    git repository. If ssh public key auth is used in the repo (e.g. gitolite, Github), each 
    destination server may then require either: (a) identical ssh keys or (b) provision each 
    destination server in the repo. Both have maintenance and security issues.

    All git operations are done on a separate ``local_tmpdir``, and not on a checkout where 
    the fabfile is located. Everytime this function is invoked, the ``repo_url`` is always
    ensured to be fresh (``git clone + git fetch``). This means only commits fetched from the
    ``repo_url`` can be deployed. 

    """
    # ensure git + rsync is available locally
    local('which git')
    local('which rsync')

    # resolve user,host,port for rsh string
    user, host, port = normalize(env.host_string)

    # ensure the temp paths are ready 
    local_user = local('whoami', capture=True)
    clone_basepath_local = os.path.join(local_tmpdir, local_user, 'deploy', host, user, str(port), 'git')
    local('mkdir -p %s' % clone_basepath_local)

    # prepare remote path strings
    clone_basepath_remote = os.path.join(home, base_dir)
    cuisine.dir_ensure(clone_basepath_remote)

    # prepare history (for recovery)
    hist = git.GitHistory()
    if save_history:
        remote_hist_path = git.get_remote_git_history_path(home)
        try:
            tmphist = git.load_remote_git_history(remote_hist_path, local_user=local_user)
            if tmphist is not None:
                hist = tmphist
        except Exception, e:
            error("Warning: Unable to load history file %s: %s" % (remote_hist_path, e ))
            
    # needed later for us to delete the unneeded repo clones
    local_clones_dirs = local('cd %s && ls' % clone_basepath_local, capture=True).split("\n")
    local_clones = { }
    for lc in local_clones_dirs:
        local_clones[lc] = True

    # clone, reset, log to history
    clone_path_remote = os.path.join(clone_basepath_remote, repo_dir)
    clone_path_local = os.path.join(clone_basepath_local, repo_dir)

    cloned_locally = local('test -d "%s" && echo OK; true' % clone_path_local, capture=True).endswith('OK')
    if not cloned_locally:
        with lcd(clone_basepath_local):
            local('git clone %s %s' % (repo_url, repo_dir))

    with lcd(clone_path_local):
        local('git fetch')
        local('git reset --hard "origin/%s"' % refspec)
        local('git submodule update --init --recursive')
        fuller_log = local('git log -n1 --pretty=fuller', capture=True)
        hist.log_latest(repo_url, refspec, repo_dir, fuller_log)

    if repo_dir in local_clones:
        del local_clones[repo_dir]

    # delete all undocumented local clones
    for lc in local_clones.keys():
        with lcd(clone_basepath_local):
            local('rm -rf %s' % lc)

    if save_history:
        cuisine.file_write(remote_hist_path, hist.dump())

    prompts = [ 'Are you sure you want to continue connecting', ".* password:" ]
    answers = [ 'yes', get_password() ]


    port_string = "-p %s" % port
    rsh_parts = [port_string]
    rsh_string = "--rsh='ssh %s'" % " ".join(rsh_parts)

    user_at_host = "%s@%s" % (user, host)

    do_delete_param = ''
    if do_delete:
        do_delete_param = '--delete-during'

    rsync_cmd = '''/bin/bash -l -c "rsync %s --exclude \".git/" -lpthrvz %s %s %s:%s"''' % (do_delete_param, rsh_string, clone_basepath_local + "/", user_at_host, clone_basepath_remote)
    local_run_expect(rsync_cmd, prompts, answers, logfile=sys.stdout)
            
    


@completed_ok(arg_output=[0,1,2])
def ssh_push(repo_url, branch, dest_name, dest_base_path='opt', host_string=None):
    """
    Deploy to remote via git push and post-receive checkout hook

    :param repo_url: *required* str; url of the git repo
    :param branch: *required* str; the git branch to checkout for deploy
    :param dest_name: *required* str; name of the directory to checkout the code to.
    :param dest_base_path: str; base dir of dest_name, default 'opt' (relative to ``$HOME``)
    :param host_string: str, the host string, will default to ``env.host_string``

    Problem statement: How do we ensure that code from a git repository gets deployed 
    uniformly, efficiently across all remote hosts.

    This is another solution to pushing code to remote servers, similar to the ``rsync()`` solution.
    Leverage ssh since fabric uses this already; we get auth + push benefits.

    And take advantage of git's post-receive hook, wherein we setup a hidden bare repo and a hook 
    to automatically checkout a working copy after pushing.

    Git is required in remote hosts, but only for handling the  post-receive checkout purpose only.

    All git operations are done on a separate per-repo local tmpdir, and not on a checkout where 
    the fabfile is located. Everytime this function is invoked, the ``repo_url`` is always
    ensured to be fresh (``git clone + git fetch``). This means only existing commits fetched from the
    ``repo_url`` can be deployed. 

    """
    if host_string is None:
        host_string = env.host_string
    
    # create local clone
    user, host, port = normalize(host_string)
    tmpprojdir = os.path.join(tempfile.gettempdir(), 'deploy', host, 'port-'+port, user )
    if not local('ls %s/%s/.git && echo OK; true' % (tmpprojdir, dest_name), capture=True).endswith('OK'):
        local('mkdir -p %s' % tmpprojdir)
        local('(cd %s && git clone -q %s %s && cd %s && git checkout branch)' % (tmpprojdir, repo_url, dest_name, dest_name, branch))
    with lcd('%s/%s' % (tmpprojdir, dest_name)):
        local('git fetch -q origin')
        local('git reset -q --hard origin/%s' % branch )
 
    user_home = run('pwd')
    run('mkdir -p %s/%s' % (dest_base_path, dest_name))
    if not run('test -d .gitpush/%s.git && echo OK; true' % dest_name ).endswith('OK'):
        ### http://caiustheory.com/automatically-deploying-website-from-remote-git-repository
        run('mkdir -p .gitpush/%s.git' % dest_name)
        with cd('.gitpush/%s.git' % dest_name):
            run('git init --bare -q')
            run('git --bare update-server-info')
            run('git config --bool core.bare false')
            run('git config --path core.worktree %s/%s/%s' % (user_home, dest_base_path, dest_name))
            run('git config receive.denycurrentbranch ignore')
            run("""echo '#!/bin/sh' > hooks/post-receive""")
            run("""echo 'git checkout -f' >> hooks/post-receive""")
            run('chmod 755 hooks/post-receive')
 
    with lcd('%s/%s' % (tmpprojdir, dest_name)):
        if not local('git remote | grep dest | head -n1', capture=True).endswith('dest'):
            local('git remote add dest ssh://%s@%s:%s%s/.gitpush/%s.git' % (user, host, port, user_home, dest_name))
        local('git push dest +master:refs/heads/%s' % branch)
    



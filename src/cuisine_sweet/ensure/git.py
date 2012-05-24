import os
import sys
import cuisine

from fabric.api import env, cd, lcd, local, run, put, abort
from fabric.utils import error
from fabric.auth import get_password

from cuisine_sweet import git
from cuisine_sweet.utils import completed_ok, local_run_expect


@completed_ok(arg_output=[0,1])
def rsync(repo_url, repo_dir, refspec='master', home='.', base_dir='git', local_tmpdir='/tmp', save_history=False):
    """
    Does a git clone locally then rsync to remote
    """
    # ensure git + rsync is available locally
    local('which git')
    local('which rsync')

    # ensure the temp paths are ready 
    local_user = local('whoami', capture=True)
    clone_basepath_local = os.path.join(local_tmpdir, local_user, 'deploy', env.host, env.user, 'git')
    local('mkdir -p %s' % clone_basepath_local)

    # prepare remote path strings
    clone_basepath_remote = os.path.join(home, base_dir)
    cuisine.dir_ensure(clone_basepath_remote)

    cuisine.command_ensure('git', package='git')

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
        local('git submodule update --init')
        local('git reset --hard "origin/%s"' % refspec)
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
    rsync_cmd = '''/bin/bash -l -c "rsync --delete --exclude \".git/" -lpthrvz --rsh='ssh -p 22' %s %s:%s"''' % (clone_basepath_local + "/", env.host_string, clone_basepath_remote)
    local_run_expect(rsync_cmd, prompts, answers, logfile=sys.stdout)
            
    

    



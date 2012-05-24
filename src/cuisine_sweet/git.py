import os
import re
import email.utils
import datetime
import time
import yaml
import cuisine
from fabric.api import env, local, run, get, abort


class GitHistory(object):
    """
    Encapsulates the history of git deploys
    """

    def __init__(self, initial_dump={ }):
        self.commits = initial_dump

    def log_latest(self, repo_url, repo_refspec, repo_dir, log):
        c = self.parse_fuller_log(log)
        if not (repo_dir in self.commits):
            self.commits[repo_dir] = [ ]
        do_append = True
        if len(self.commits[repo_dir]) > 0:
            # try to check first if the last commit is identical to this commit
            last_c = self.commits[repo_dir][0][2]['commit_hash']
            if last_c == c['commit_hash']:
                # ignore dups
                do_append = False 
                # but update last deploy timestamp
                self.commits[repo_dir][0][0] = time.time()

        if do_append:    
            self.commits[repo_dir].insert(0, [ time.time(), [ repo_url, repo_refspec, repo_dir ], c ])

    def dump(self):
        return yaml.dump(self.commits)


    def repo_history(self, repo_dir):
        if repo_dir in self.commits:
            return self.commits[repo_dir]
        return None


    def parse_fuller_log(self, log):
        lines = log.split("\n")
        chash = lines.pop(0).split(' ')[1]
        if re.match(r'Merge', lines[0]):
            lines.pop(0)
        author = re.match(r'Author:\s+(.*)$', lines.pop(0)).group(1)
        date_raw = re.match(r'AuthorDate:\s+(.*)$', lines.pop(0)).group(1)
        date_p = email.utils.parsedate_tz(date_raw)
        date_args = date_p[0:6] + tuple([date_p[9]])
        date = datetime.datetime(*date_args)
        lines.pop(0)
        lines.pop(0)
        lines.pop(0)
        title = lines.pop(0)
        message_body = [ ]
        if len(lines) > 0:
            lines.pop(0)
            message_body = lines
        return { 'commit_hash': chash, 
                 'author': author, 
                 'date': date, 
                 'title': title, 
                 'message_body': message_body,
                 }



# ======================

def get_remote_git_history_path(home, filename='history.yml'):
    """
    returns the string path to the remote git history file
    """
    remote_hist_dir = os.path.join(home, '.deploy', 'git')
    run('mkdir -p %s' % remote_hist_dir)
    remote_hist_path = os.path.join(remote_hist_dir, 'history.yml')
    return remote_hist_path


def load_remote_git_history(remote_hist_path, local_user=None, tmpdir='/tmp'):
    if not local_user:
        local_user = local('whoami', capture=True)
    hist = None
    if cuisine.file_exists(remote_hist_path):
        tmp_history_path = os.path.join(tmpdir, local_user, 'deploy', env.host, env.user, 'git-history')
        local('mkdir -p %s' % tmp_history_path)
        # download
        downloaded = get(remote_hist_path, local_path=tmp_history_path)
        hist_dump_yml = open(downloaded[0]).read()
        local('rm %s' % downloaded[0])
        # try loading the history dump
        hist_dump = yaml.load(hist_dump_yml)
        hist = GitHistory(initial_dump=hist_dump)
    return hist



def history_show_commits(repo_dir, limit=10, home='.'):
    """
    params(repo_dir, limit=10)
    """
    remote_hist_path = get_remote_git_history_path(home)
    hist = load_remote_git_history(remote_hist_path)
    if not hist:
        abort("No history found")

    repo_history = hist.repo_history(repo_dir)
    print yaml.dump(repo_history[0:limit])
    



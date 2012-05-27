Basic Usage
-----------

``cuisine_sweet`` is to be used in tandem with ``fabric``.

To illustrate usage, see the sample ``fabfile.py`` below::

    from fabric.api import task, env
    from cuisine_sweet import ensure
    
    env.hosts = [ 'myproject@server1.example.com', 'myproject@server2.example.com' ]

    @task
    def initial():
        ensure.yum.package_installed('gcc')
        ensure.yum.package_installed('make')
        ensure.yum.package_installed('git')
        ensure.yum.package_installed('python')
        ensure.yum.package_installed('python-devel')
        ensure.supervisord.installed()

    @task
    def deploy():
        ensure.local_git.up_to_date(against='origin/master')
        ensure.local_git.clean()
        ensure.git.rsync('git@ourgit.example.com:myproject.git', 'myproject', refspec='master', base_dir='git')
        ensure.user_crontab.loaded('git/myproject/user.cron')
        ensure.supervisord.running('git/myproject/supervisord.conf', '/tmp/myproject.supervisord.pid')
        ensure.supervisord.updated_with_latest_config('git/myproject/supervisord.conf')




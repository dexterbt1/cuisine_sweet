# cuisine\_sweet

Sugar-coated declarative recipes built on top of [http://fabfile.org](Fabric) and [https://github.com/sebastien/cuisine](Cuisine)

# Sample fabfile.py

    from fabric.api import task, env
    from cuisine_sweet import ensure
    
    env.hosts = [ 'myproject@example.com' ]

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


# Ensure Modules

* git
* local\_git
* yum
* supervisord
* user\_crontab
* fs
* cpan\_module
* git


# Warning

This is experimental alpha-quality stuff. The API and implementation are still highly fluid and continuously evolving.
See LICENSE file for more information

# References

* Fabric - http://fabfile.org
* Cuisine - https://github.com/sebastien/cuisine


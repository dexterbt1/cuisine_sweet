# cuisine\_sweet

Sugar-coated declarative deployment recipes built on top of [Fabric](http://fabfile.org) and [Cuisine](https://github.com/sebastien/cuisine)


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


# Installation

This module is available on PyPI and via Github directly.

* Using pip: `pip install cuisine_sweet`
* Using setuptools: `easy_install cuisine_sweet`
* Or clone this repository and do a `python setup install`


# Ensure Modules

At the heart of `cuisine_sweet` is the collection of ensure modules. These modules encapsulate
what is being checked/deployed (declarative), without specifying the how and the where parts
(imperative). An ensure API is an assertion in the form: ensure.object.state(params)

* git - rsync-style git deployment
* local\_git - assertions on the current git repo of the fabfile
* yum - yum package management
* supervisord - service management via supervisord
* user\_crontab - user's crontab file/state assertions
* fs - filesystem related checks/assertions
* cpan\_module - locallib-flavored perl CPAN module deployments


# Warning

This is experimental alpha-quality stuff. The API and implementation are still highly fluid and continuously evolving.
See LICENSE file for more information.


# References

* Fabric - http://fabfile.org
* Cuisine - https://github.com/sebastien/cuisine


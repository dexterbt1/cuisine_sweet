*************
cuisine_sweet
*************

Sugar-coated declarative deployment recipes built on top of `Fabric <http://fabfile.org>`_ 
and `Cuisine <https://github.com/sebastien/cuisine>`_.

With Fabric's low-level remote ssh orchestration and Cuisine's generic recipes; the goal
is to build a collection of wrappers capturing various, usually opinionated, system deployment 
styles.

At the heart of ``cuisine_sweet`` is the collection of ``ensure`` modules. These modules encapsulate
what is being checked/deployed (declarative), without specifying the how and the where parts
(imperative). An ensure is both an assertion check + action-if-needed in the form: 
``ensure.object.state(params)``. 


Sample Usage
------------

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


References
----------

- `Source Code <http://github.com/dexterbt1/cuisine_sweet>`_
- `Documentation <http://cuisine_sweet.readthedocs.org/>`_
- Feedback / Patches - `Create an issue <http://github.com/dexterbt1/cuisine_sweet/issues>`_


Copyright © 2012, Dexter B. Tad-y


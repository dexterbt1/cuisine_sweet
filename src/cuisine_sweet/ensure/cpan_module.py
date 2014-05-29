"""
Fabfile functions for ensuring the state of CPAN modules
"""

import os
import pipes
import cuisine

from fabric.api import run, puts, env, prefix
from fabric.colors import green, blue
from cuisine_sweet.utils import completed_ok

def perl_config_archname():
    return run("perl -MConfig -e 'print $Config{archname}'")


def cpanm_bin_installed(home='/tmp'):
    cuisine.select_package(option='yum')
    cuisine.package_ensure('perl-devel')
    binpath = '%s/.deploy/bin' % home
    cpanm = '%s/cpanm' % binpath
    if not cuisine.file_exists(cpanm):
        cuisine.dir_ensure(binpath, recursive=True, mode=755)
        cuisine.package_ensure('curl')
        run('curl -kL http://cpanmin.us > %s' % cpanm)
        run('chmod 755 %s' % cpanm)
        cuisine.file_exists(cpanm)
    return cpanm


def _exists(module_name, home='/tmp', perlarch=None, locallib='perl5'):
    path1 = os.path.join(home, locallib, 'lib', 'perl5')
    path2 = os.path.join(home, locallib, 'lib', 'perl5', perlarch)
    result = run("perl -I %s -I %s -e 'use %s' >& /dev/null && echo OK; true" % (path1, path2, module_name))
    return result.endswith('OK')


def _do_install(module_name, home='/tmp', cpanm='/tmp/.deploy/bin/cpanm', source=None, locallib='perl5'):
    mod = module_name
    if source is not None:
        mod = source
    locallib_base = os.path.join(home, locallib)
    opts = '-l %s' % locallib_base
    with prefix('export AUTOMATED_TESTING=1 PERL_MM_NONINTERACTIVE=1'):
        run('%s %s %s' % (cpanm, opts, mod))


def _prepare_environment():
    # --- perl arch name
    arch = perl_config_archname()
    if 'perl_arch' not in env:
        env.perl_arch = { }
    env.perl_arch[env.host] = arch
    # --- cpanm
    cpanm = cpanm_bin_installed(home='.')
    if 'cpanm_bin' not in env:
        env.cpanm_bin = { }
    env.cpanm_bin[env.host] = cpanm
    

@completed_ok(arg_output=[0])
def installed(module, source=None, locallib='perl5', home='.'):
    """
    Ensure that the Perl CPAN Module installed (in a localized locallib path)

    :param module: *required* str; the name of the CPAN module to check/install
    :param source: str; the url to the CPAN dist tarball
    :param locallib: str; the directory name for locallib
    :param home: str; the base directory where locallib

    Modules are expected to be located under a `local::lib <http://search.cpan.org/perldoc?local::lib>`_
    directory. If the module is not found, then it is automatically installed using a copy of
    `cpanm <http://search.cpan.org/perldoc?App::cpanminus>`_.

    Ths full path of the locallib is derived from ``home + locallib``, 
    which defaults to ``./perl5`` of the remote user. 

    Scripts relying on the modules installed under the locallib will (at the minimum) need to
    set their shell environment variables (typically via ``source path/to/my_env_source_file``:

    .. code-block:: sh

        # myenv.source; either source this or add these lines somewhere ... e.g. ~/.bashrc
        export LOCALLIB="perl5"
        export PERL5ARCH=`perl -MConfig -e 'print $Config{archname}'`
        export PERL5LIB="$HOME/$LOCALLIB/lib/perl5:$HOME/$LOCALLIB/lib/perl5/$PERL5ARCH:$HOME/$LOCALLIB/lib/perl5/$PERL5ARCH/auto/"
    """
    try:
        perlarch = env.perl_arch[env.host]
        cpanm = env.cpanm_bin[env.host]
    except:
        _prepare_environment()
        perlarch = env.perl_arch[env.host]
        cpanm = env.cpanm_bin[env.host]
    if not _exists(module, home=home, perlarch=perlarch, locallib=locallib):
        _do_install(module, home=home, cpanm=cpanm, source=source, locallib=locallib)


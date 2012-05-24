"""
Fabric checks and assertions for CPAN modules
"""

import os
import cuisine

from fabric.api import run, puts, env
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
        run('curl -L http://cpanmin.us > %s' % cpanm)
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
    Ensure that the cpan module installed (in a localized locallib path)
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



"""
Fabric checks and assertions for RHEL-flavored yum installations
"""

import cuisine 
from fabric.api import run, sudo
from cuisine_sweet.utils import completed_ok


@completed_ok(arg_output=[0])
def grouppackage_installed(groupname):
    """
    Ensure that the group package named `groupname` is installed.

    If the groupname is not installed, then it will be installed
    using sudo('yum -y groupinstall ...')
    """
    grp_installed = run('yum grouplist installed "%s" | grep -i installed && echo OK; true' % groupname).endswith('OK')
    if not grp_installed:
        sudo('yum -y groupinstall "%s"' % groupname)


@completed_ok(arg_output=[0])
def package_installed(package):
    """
    Ensure that a package named `package` is installed.

    Wraps cuisine.package_ensure() + select_package(option='yum')
    """
    cuisine.select_package(option='yum')
    cuisine.package_ensure(package)



from spack import *


class PySupervisord(PythonPackage):
    """
       Supervisor: A Process Control System
       Supervisor is a client/server system that allows its users 
       to monitor and control a number of processes on UNIX-like 
       operating systems
    """

    homepage = "http://supervisord"
    url      = "https://files.pythonhosted.org/packages/97/48/f38bf70bd9282d1a18d591616557cc1a77a1c627d57dff66ead65c891dc8/supervisor-4.0.3.tar.gz"

    version('4.0.3', sha256='f768abc073e8702892718938b8a0ab98ebcb91c2afcb39bf2cb570d3eb51149e')

    depends_on('py-setuptools', type='build')
    depends_on('py-meld3',      type=('build', 'run'))
    depends_on('py-pytest',     type='test')
    depends_on('py-pytest-cov', type='test')

from spack import *

class PyPythonCrontab(PythonPackage):
    """Python package for managing crontab files"""

    homepage = "http://www.example.com"
    url      = "https://files.pythonhosted.org/packages/2c/4f/60b3481b00af6cb91eb19bfb14ac518aebd268fa2a0cd3e21ba1687c4816/python-crontab-2.3.6.tar.gz"

    version('2.3.6', 'e7f70f37e57080b8e837e6aed1c8fad8')

    depends_on('py-setuptools',   type='build')


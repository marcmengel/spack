
from spack import *


class PyMeld3(PythonPackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://github.com/supervisor/meld3"
    url      = "https://files.pythonhosted.org/packages/45/a0/317c6422b26c12fe0161e936fc35f36552069ba8e6f7ecbd99bbffe32a5f/meld3-1.0.2.tar.gz"

    version('1.0.2', sha256='f7b754a0fde7a4429b2ebe49409db240b5699385a572501bb0d5627d299f9558')

    depends_on('py-setuptools', type='build')


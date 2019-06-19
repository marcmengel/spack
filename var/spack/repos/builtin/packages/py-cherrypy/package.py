from spack import *

class PyCherrypy(PythonPackage):
    """CherryPy is a pythonic, object-oriented HTTP framework."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://cherrypy.org/"
    url      = "https://files.pythonhosted.org/packages/1f/de/3327bd7168be762180924085fecef2e127d128f1d6157f88cd87fdac2971/CherryPy-18.1.1.tar.gz"

    # FIXME: Add proper versions and checksums here.
    version('18.1.1', '76e5d3c6b7be845345f871c604cfdf58')

    # FIXME: Add dependencies if required.
    depends_on('py-setuptools', type='build')
    depends_on('py-docutils', type='build')

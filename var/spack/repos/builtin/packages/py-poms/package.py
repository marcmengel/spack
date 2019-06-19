from spack import *

class PyPoms(PythonPackage):
    """Production Operations Management System"""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "http://cdcvs.fnal.gov/redmine/projects/prod_mgmt_db"
    url = 'http://cdcvs.fnal.gov/cgi-bin/git_archive.cgi/cvs/projects/prod_mgmt_db.v4_1_0.tar'

    # FIXME: Add proper versions and checksums here.
    version('4_1_2', '8c44623b2fcc78ac2120fb5a185917de')
    version('4_1_0', 'c8682135a0d4eae8df00a29ececb6020')

    depends_on('python',               type=('build','run'))
    depends_on('py-setuptools',        type=('build', 'run'))
    depends_on('py-psycopg2',          type=('build', 'run'))
    depends_on('py-cherrypy',          type=('build', 'run'))
    depends_on('py-sqlalchemy',        type=('build', 'run'))
    depends_on('py-jinja2',            type=('build', 'run'))
    depends_on('py-python-crontab',    type=('build', 'run'))
    depends_on('py-futures',           type=('build', 'run'))
    depends_on('py-prometheus-client', type=('build', 'run'))


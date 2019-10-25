from spack import *

class PyPoms(PythonPackage):
    """POMS: Fermilab Production Operations Management System"""

    homepage = "http://cdcvs.fnal.gov/redmine/projects/prod_mgmt_db"
    url = 'http://cdcvs.fnal.gov/cgi-bin/git_archive.cgi/cvs/projects/prod_mgmt_db.v4_1_0.tar'

    version('4_1_2', '8c44623b2fcc78ac2120fb5a185917de')
    version('4_1_0', 'c8682135a0d4eae8df00a29ececb6020')
    version('4_2_0', 'cf496f78f5e988684d32afa352b0c77b')

    depends_on('python',               type=('build','run'))
    depends_on('py-cherrypy',          type=('build', 'run'))
    depends_on('py-futures',           type=('build', 'run'))
    depends_on('py-jinja2',            type=('build', 'run'))
    depends_on('py-more-itertools',    type=('build', 'run'))
    depends_on('py-prometheus-client', type=('build', 'run'))
    depends_on('py-psycopg2',          type=('build', 'run'))
    depends_on('py-python-crontab',    type=('build', 'run'))
    depends_on('py-requests',          type=('build', 'run'))
    depends_on('py-setuptools',        type=('build', 'run'))
    depends_on('py-sqlalchemy',        type=('build', 'run'))

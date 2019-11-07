# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack import *


class PyCheroot(PythonPackage):
    """ Highly-optimized, pure-python HTTP server """

    homepage = "https://cheroot.cherrypy.org/"
    url      = "https://pypi.io/packages/source/c/cheroot/cheroot-6.5.5.tar.gz"

    version(
        '6.5.5', sha256='f6a85e005adb5bc5f3a92b998ff0e48795d4d98a0fbb7edde47a7513d4100601')

    depends_on('py-setuptools', type='build')
    depends_on('py-setuptools-scm@1.15.0:', type='build')
    depends_on('py-setuptools-scm-git-archive@1.0:', type='build')
    depends_on('py-more-itertools@2.6', type=('build', 'run'))
    depends_on('py-six@1.11.0', type=('build', 'run'))
    depends_on('py-backports-functools-lru-cache', type=('build', 'run'))

# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install py-python-crontab
#
# You can edit this file again by typing:
#
#     spack edit py-python-crontab
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *


class PyPythonCrontab(PythonPackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "http://www.example.com"
    url      = "https://files.pythonhosted.org/packages/2c/4f/60b3481b00af6cb91eb19bfb14ac518aebd268fa2a0cd3e21ba1687c4816/python-crontab-2.3.6.tar.gz"

    version('2.3.6', 'e7f70f37e57080b8e837e6aed1c8fad8')

    depends_on('py-setuptools',   type='build')


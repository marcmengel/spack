# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyPrometheusClient(PythonPackage):
    """Prometheus instrumentation library for Python applications."""

    homepage = "https://pypi.org/project/prometheus_client/"
    url      = "https://pypi.io/packages/source/p/prometheus_client/prometheus_client-0.5.0.tar.gz"

    version('0.5.0', sha256='e8c11ff5ca53de6c3d91e1510500611cafd1d247a937ec6c588a0a7cc3bef93c')

    depends_on('py-setuptools', type='build')

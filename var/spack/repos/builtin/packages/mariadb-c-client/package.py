##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *


class MariadbCClient(CMakePackage):
    """MariaDB turns data into structured information in a wide array of
    applications, ranging from banking to websites. It is an enhanced,
    drop-in replacement for MySQL. MariaDB is used because it is fast,
    scalable and robust, with a rich ecosystem of storage engines,
    plugins and many other tools make it very versatile for a wide
    variety of use cases. This package comprises only the standalone 'C
    Connector', which enables connections to MariaDB and MySQL servers.
    """

    homepage = "http://mariadb.org/about/"
    url      = "https://downloads.mariadb.com/Connectors/c/connector-c-3.0.3/mariadb-connector-c-3.0.3-src.tar.gz"

    version('3.0.3', '666df28c42988cedc3dec1e1c0da5212')

    provides('mariadb-c')
    provides('mysql-c')

    depends_on('cmake@2.6:', type='build')
    depends_on('curl')
    depends_on('pcre')
    depends_on('openssl')
    depends_on('zlib')

    def cmake_args(self):
        args = ['-DWITH_EXTERNAL_ZLIB=ON', '-DWITH_MYSQLCOMPAT=ON']
        return args

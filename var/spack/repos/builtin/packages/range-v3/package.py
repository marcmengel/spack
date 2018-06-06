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


class RangeV3(CMakePackage):
    """Range v3 forms the basis of a proposal to add range support to the
    standard library (N4128: Ranges for the Standard Library). It also will
    be the reference implementation for an upcoming Technical
    Specification. These are the first steps toward turning ranges into an
    international standard."""

    homepage = "https://github.com/ericniebler/range-v3"
    url      = "https://github.com/ericniebler/range-v3/archive/0.3.6.tar.gz"

    version('0.3.6', '1a781c28acba501e76a4b04da62645ab')
    version('0.3.5', '22f34c74f37a32cb9f2e76869cba27f5')
    version('0.3.0', '7fb74afbddec3e166739e635f5b365f2')

    depends_on('cmake@3.6:', type='build')
    depends_on('doxygen+graphviz', type='build')
    depends_on('git', type='build')

    # Note that as of 0.3.6 range is a header-only library so it is not
    # necessary to match standards with packages using this
    # one. Eventually range-v3 will be obsoleted by the C++ statndard.
    variant('cxxstd',
            default='11',
            values=('11', '14', '17'),
            multi=False,
            description='Use the specified C++ standard when building.')

    # Known compiler conflicts. Your favorite compiler may also conflict
    # depending on its C++ standard support.
    conflicts('%clang@:3.6.1')
    conflicts('%gcc@:4.9.0')
    conflicts('%gcc@:5.2.0', when='cxxstd=14')
    conflicts('%gcc@:5.99.99', when='cxxstd=17')

    def cmake_args(self):
        args = ['-DRANGES_CXX_STD={0}'.
                format(self.spec.variants['cxxstd'].value)]
        return args

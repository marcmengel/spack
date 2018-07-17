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
import os
import sys


class Root(CMakePackage):
    """ROOT is a data analysis framework."""

    homepage = "https://root.cern.ch"
    url      = "https://root.cern.ch/download/root_v6.09.02.source.tar.gz"

    # Production versions
    version('6.14.00', '3613c930589734531ac8995486d41af5')

    # Old versions
    version('6.12.06', 'bef6535a5d0cdf471b550da45a10f605')
    version('6.12.04', '8529b4c4e2befe8bdaa343a8e5d7534c')
    version('6.12.02', 'a46d67cf473f2137b5a3a9849f8170da')
    version('6.10.08', '48f5044e9588d94fb2d79389e48e1d73')
    version('6.10.06', '3a5f846883822e6d618cc4bd869b2ece')
    version('6.10.04', 'e6e54fd2b5ebc2610c9aa0d396b7522d')
    version('6.10.02', '19f2285c845a48355db779938fb4db99')
    version('6.10.00', 'c2f0dfe9588b8b8919e48155a0e34aed')
    version('6.08.06', 'bcf0be2df31a317d25694ad2736df268')
    version('6.08.04', '982f64c489e52b7e2203918cd0438ceb')
    version('6.08.02', '50c4dbb8aa81124aa58524e776fd4b4b')
    version('6.08.00', '8462a530d27fa5ca7718ea4437632c3c')
    version('6.06.08', '6ef0fe9bd9f88f3ce8890e3651142ee4')
    version('6.06.06', '4308449892210c8d36e36924261fea26')
    version('6.06.04', '55a2f98dd4cea79c9c4e32407c2d6d17')
    version('6.06.02', 'e9b8b86838f65b0a78d8d02c66c2ec55')
    version('6.06.00', '65675a1dbaa4810df0479dbcf62f0ba0')
    version('6.04.18', '3ac4e284fac6b2bf477100f7b0e721e0')
    version('6.04.16', '4bc634f060ac0d145447ced40039848a')
    version('6.04.14', 'f0fe83b2e69fccf5d54d448cbede7c79')
    version('6.04.12', 'bb43d3c01d97cd2714e841630148c371')
    version('6.04.10', '76145a2571b25f2faf1456536c906bf5')
    version('6.04.08', '0c4861a5e439b6e4a40bc655bd5b784b')
    version('6.04.06', 'e649ce9430df2d87786527ec8196e2ea')
    version('6.04.04', '95cdb2ae01b55c6ea450b4b248a1c987')
    version('6.04.02', '00c242fc9833677310858346fd768938')
    version('6.04.00', 'ead93da34ad0f017e630e62721aae91c')
    # No reliable CMake-based build prior to 6.04/00.

    patch('format-stringbuf-size.patch', level=0)
    patch('find-mysql.patch', level=1)
    patch('honor-unuran-switch.patch', level=1, when='@:6.13.99')

    if sys.platform == 'darwin':
        patch('math_uint.patch', when='@6.06.02')
        patch('root6-60606-mathmore.patch', when='@6.06.06')

    variant('python', default=True, description='Build with python support')
    variant('graphviz', default=False, description='Enable graphviz support')
    variant('pythia6', default=False, description='Build Pythia6 plugin.')
    variant('pythia8', default=False, description='Build Pythia8 plugin.')

    variant('cxxstd',
            default='11',
            values=('11', '14', '17'),
            multi=False,
            description='Use the specified C++ standard when building.')

    depends_on('cmake@3.4.3:', type='build')
    depends_on('pkgconfig',   type='build')

    depends_on('blas')
    depends_on('cfitsio')
    depends_on('fftw')
    depends_on('freetype')
    depends_on('gl2ps')
    depends_on('glew')
    depends_on('graphviz', when='+graphviz')
    depends_on('gsl')
    depends_on('jpeg')
    depends_on('libice')
    depends_on('libpng')
    depends_on('libsm')
    depends_on('libx11')
    depends_on('libxext')
    depends_on('libxft')
    depends_on('libxml2+python', when='+python')
    depends_on('libxml2~python', when='~python')
    depends_on('libxpm')
    depends_on('lz4', when='@6.13.02:')  # See cmake_args, below.
    depends_on('mysql-c')
    depends_on('openssl')
    depends_on('pcre')
    depends_on('postgresql-c')
    depends_on('pythia6', when='+pythia6')
    depends_on('pythia8', when='+pythia8')
    depends_on('python@2.7:')
    depends_on('sqlite')
    depends_on('tbb')
    depends_on('xrootd')
    depends_on('xxhash', when='@6.13.02:')  # See cmake_args, below.
    depends_on('xz')
    depends_on('zlib')

    # Per correspondence on root-planning@cern.ch list, 2018-05-02/03.
    conflicts('%intel', when='cxxstd=17')
    conflicts('%intel@:16.99', when='cxxstd=14')
    conflicts('%intel@:15.99', when='cxxstd=11')
    conflicts('%intel', when='@:6.09.99')

    def cmake_args(self):
        options_on = [
            'fitsio',
            'fortran',
            'gminimal',
            'fail-on-missing',
            'mysql',
            'sqlite',
            'x11'
        ]
        options_off = [
            'afs',
            'alien',
            'astiff',
            'bonjour',
            'castor',
            'cocoa',
            'davix',
            'dcache',
            'geocad',
            'gfal',
            'glite',
            'globus',
            'gvis',
            'hdfs',
            'jemalloc',
            'krb5',
            'ldap',
            'monalisa',
            'odbc',
            'oracle',
            'pythia8',
            'qt',
            'qtgsi',
            'r',
            'rfio',
            'root7',
            'ruby',
            'sapdb',
            'srp',
            'tcmalloc',
            'unuran',
            'vc',
            'veccore',
            'vecgeom',
            'xft'
        ]
        # Built-in LLVM / Clang is necessary for now: Root build has
        # local enhancements to Clang. AfterImage and FTGL are moribund
        # packages.
        builtin_on = [
            'afterimage',
            'ftgl',
            'llvm',
        ]
        # Everything else should be found externally.
        builtin_off = [
            'cfitsio',
            'davix',
            'fftw3',
            'freetype',
            'gl2ps',
            'glew',
            'gsl',
            'lzma',
            'openssl',
            'pcre',
            'unuran',
            'vc',
            'vdt',
            'veccore',
            'xrootd',
            'zlib'
        ]

        # Deal with python bindings.
        if self.spec.satisfies('+python ^python@2.7:2.99.99'):
            options_on.append('python')
            options_off.append('python3')
        elif self.spec.satisfies('+python ^python@3.0:'):
            options_off.append('python')
            options_on.append('python3')
        else:
            options_off.append('python')
            options_off.append('python3')

        # Build system / code weirdness requires Root's builtin LZ4 for
        # some versions.
        bo_ref = builtin_on if self.spec.satisfies('@6.12.02:6.12.99') else \
            builtin_off
        bo_ref.extend(['xxhash', 'lz4'])

        # Optional support for Pythia6
        bo_ref = options_on if '+pythia6' in self.spec else options_off
        bo_ref.append('pythia6')

        # Optional support for Pythia8
        bo_ref = options_on if '+pythia8' in self.spec else options_off
        bo_ref.append('pythia8')

        # Turn our settings into CMake variable settings.
        args = ['-D{0}=ON'.format(x) for x in options_on] + \
               ['-D{0}=OFF'.format(x) for x in options_off] + \
               ['-Dbuiltin_{0}=ON'.format(x) for x in builtin_on] + \
               ['-Dbuiltin_{0}=OFF'.format(x) for x in builtin_off]

        if sys.platform == 'darwin':
            if self.compiler.cc == "gcc":
                args.extend([
                    x.format('-D__builtin_unreachable=__builtin_trap')
                    for x in ('-DCMAKE_C_FLAGS={0}',
                              '-DCMAKE_CXX_FLAGS={0}')])

        args.append('-Dcxx{0}=ON'.format(self.spec.variants['cxxstd'].value))
        if 'mysql-c' in self.spec:
            args.append('-DCMAKE_PROGRAM_PATH={0}'.format(
                os.path.join(self.spec['mysql-c'].prefix, 'bin')))
        return args

    def setup_environment(self, spack_env, run_env):
        run_env.set('ROOTSYS', self.prefix)
        run_env.set('ROOT_VERSION', 'v{0}'.format(self.version.up_to(1)))
        run_env.prepend_path('PYTHONPATH', self.prefix.lib)
        if 'lz4' in self.spec:
            spack_env.append_path('CMAKE_PREFIX_PATH',
                                  self.spec['lz4'].prefix)

    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        spack_env.set('ROOTSYS', self.prefix)
        spack_env.set('ROOT_VERSION', 'v{0}'.format(self.version.up_to(1)))
        spack_env.prepend_path('PYTHONPATH', self.prefix.lib)
        run_env.set('ROOTSYS', self.prefix)
        run_env.set('ROOT_VERSION', 'v{0}'.format(self.version.up_to(1)))
        run_env.prepend_path('PYTHONPATH', self.prefix.lib)

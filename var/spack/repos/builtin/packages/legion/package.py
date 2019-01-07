# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack import *


class Legion(CMakePackage):
    """Legion is a data-centric parallel programming system for writing
       portable high performance programs targeted at distributed heterogeneous
       architectures. Legion presents abstractions which allow programmers to
       describe properties of program data (e.g. independence, locality). By
       making the Legion programming system aware of the structure of program
       data, it can automate many of the tedious tasks programmers currently
       face, including correctly extracting task- and data-level parallelism
       and moving data around complex memory hierarchies. A novel mapping
       interface provides explicit programmer controlled placement of data in
       the memory hierarchy and assignment of tasks to processors in a way
       that is orthogonal to correctness, thereby enabling easy porting and
       tuning of Legion applications to new architectures.
    """
    homepage = "http://legion.stanford.edu/"
    url      = "https://github.com/StanfordLegion/legion/tarball/legion-17.02.0"
    git      = "https://github.com/StanfordLegion/legion.git"

    version('develop', branch='master')
    version('18.05.0', 'ab5ac8cd4aa4c91e6187bf1333a031bf')
    version('18.02.0', '14937b386100347b051a5fc514636353')
    version('17.10.0', 'ebfc974dc82a9d7f3ba53242ecae62e1')
    version('17.08.0', 'acc1ea8c564c4a382a015e0c9cf94574')
    version('17.02.0', '31ac3004e2fb0996764362d2b6f6844a')

    variant('mpi', default=True,
            description='Build on top of mpi conduit for mpi inoperability')
    variant('shared', default=True, description='Build shared libraries')

    depends_on("cmake@3.1:", type='build')
    depends_on("gasnet~aligned-segments~pshm segment-mmap-max='16GB'", when='~mpi')
    depends_on("gasnet~aligned-segments~pshm segment-mmap-max='16GB' +mpi", when='+mpi')

    def cmake_args(self):
        options = [
            '-DLegion_USE_GASNet=ON',
            '-DLegion_BUILD_EXAMPLES=ON',
            '-DBUILD_SHARED_LIBS=%s' % ('+shared' in self.spec)]

        if '+mpi' in self.spec:
            options.append('-DGASNet_CONDUIT=mpi')

        return options

# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
from spack.paths import spack_root


class GobjectIntrospection(Package):
    """The GObject Introspection is used to describe the program APIs and
    collect them in a uniform, machine readable format.Cairo is a 2D graphics
    library with support for multiple output"""

    homepage = "https://wiki.gnome.org/Projects/GObjectIntrospection"
    url      = "http://ftp.gnome.org/pub/gnome/sources/gobject-introspection/1.49/gobject-introspection-1.49.2.tar.xz"

    version('1.49.2', 'c47a76b05b2d8438089f519922180747')
    version('1.48.0', '01301fa9019667d48e927353e08bc218')

    depends_on("glib@2.49.2:", when="@1.49.2:")
    # version 1.48.0 build fails with glib 2.49.4
    depends_on("glib@2.48.1", when="@1.48.0")
    depends_on("python")
    depends_on("cairo")
    depends_on("bison", type="build")
    depends_on("flex", type="build")
    depends_on("pkgconfig", type="build")

    # GobjectIntrospection does not build with sed from darwin:
    depends_on('sed', when='platform=darwin', type='build')

    # This package creates several scripts from
    # toosl/g-ir-tool-template.in.  In their original form these
    # scripts end up with a sbang line like
    #
    # `#!/usr/bin/env /path/to/spack/python`.
    #
    # These scripts are generated and then used as part of the build
    # (other packages also use the scripts after they've been
    # installed).
    #
    # The path to the spack python can become too long.  Because these
    # tools are used as part of the build, the normal hook that fixes
    # this problem can't help us.
    # This package fixes the problem in two steps:
    # - it rewrites the g-ir-tool-template so that its sbang line
    #   refers directly to spack's python (filter_file step below); and
    # - it patches the Makefile.in so that the generated Makefile has an
    #   extra sed expression in its TOOL_SUBSTITUTION that results in
    #   an `#!/bin/bash /path/to/spack/bin/sbang` unconditionally being
    #   inserted into the scripts as they're generated.
    patch("sbang.patch")

    def install(self, spec, prefix):
        configure("--prefix=%s" % prefix)
        # we need to filter this file to avoid an overly long hashbang line
        filter_file('#!/usr/bin/env @PYTHON@', '#!@PYTHON@',
                    'tools/g-ir-tool-template.in')
        make()
        make("install")

    def setup_environment(self, spack_env, run_env):
        spack_env.set('SPACK_SBANG', "%s/bin/sbang" % spack_root)

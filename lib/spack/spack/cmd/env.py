# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from __future__ import print_function

import argparse
import os

import llnl.util.tty as tty
import spack.build_environment as build_env
import spack.cmd
import spack.cmd.common.arguments as arguments
from spack.util.environment import dump_environment, pickle_environment

description = "run a command in a spec's install environment, " \
              "or dump its environment to screen or file"
section = "build"
level = "long"


def setup_parser(subparser):
    arguments.add_common_arguments(subparser, ['clean', 'dirty'])
    subparser.add_argument(
        '--dump', action='store_true', default=False,
        help="instead of a command, last argument specifies a file to which "
        "to write a source-able script to replicate the environment."
    )
    subparser.add_argument(
        '--pickle', action='store_true', default=False,
        help="instead of a command, last argument is a file to which to write "
        "a pickled environment dictionary."
    )
    subparser.add_argument(
        'spec', nargs=argparse.REMAINDER,
        help="specs of package environment to emulate")


def env(parser, args):
    if not args.spec:
        tty.die("spack env requires a spec.")

    # Specs may have spaces in them, so if they do, require that the
    # caller put a '--' between the spec and the command to be
    # executed.  If there is no '--', assume that the spec is the
    # first argument.
    sep = '--'
    if sep in args.spec:
        s = args.spec.index(sep)
        spec = args.spec[:s]
        cmd = args.spec[s + 1:]
    else:
        spec = args.spec[0]
        cmd = args.spec[1:]

    specs = spack.cmd.parse_specs(spec, concretize=True)
    if len(specs) > 1:
        tty.die("spack env only takes one spec.")
    spec = specs[0]

    build_env.setup_package(spec.package, args.dirty)

    if args.dump:
        if cmd and len(cmd) == 1:
            dump_environment(cmd[0])
        else:
            tty.die("--dump requires a single file to which to dump "
                    "the environment")

    elif args.pickle:
        if cmd and len(cmd) == 1:
            pickle_environment(cmd[0])
        else:
            tty.die("--dump requires a single file to which to dump "
                    "the environment")

    elif not cmd:
        # If no command act like the "env" command and print out env vars.
        for key, val in os.environ.items():
            print("%s=%s" % (key, val))

    else:
        # Otherwise execute the command with the new environment
        os.execvp(cmd[0], cmd)

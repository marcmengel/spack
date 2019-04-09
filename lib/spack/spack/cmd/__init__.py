# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from __future__ import print_function

import itertools
import os
import re
import sys
import argparse

import llnl.util.tty as tty
from llnl.util.lang import attr_setdefault, index_by
from llnl.util.tty.colify import colify
from llnl.util.tty.color import colorize
from llnl.util.filesystem import working_dir

import spack.config
import spack.extensions
import spack.paths
import spack.spec
import spack.store
from spack.error import SpackError


# cmd has a submodule called "list" so preserve the python list module
python_list = list

# Patterns to ignore in the commands directory when looking for commands.
ignore_files = r'^\.|^__init__.py$|^#'

SETUP_PARSER = "setup_parser"
DESCRIPTION = "description"


def python_name(cmd_name):
    """Convert ``-`` to ``_`` in command name, to make a valid identifier."""
    return cmd_name.replace("-", "_")


def cmd_name(python_name):
    """Convert module name (with ``_``) to command name (with ``-``)."""
    return python_name.replace('_', '-')


#: global, cached list of all commands -- access through all_commands()
_all_commands = None
_default_command_path = spack.paths.command_path


def all_commands(command_list, command_path=None):
    """Get a sorted list of all spack commands at the specified path.

    This will list the command_path directory and find the commands
    there to construct the list.  It does not actually import the python
    files - just gets the names. The names are cached in command_list.
    """
    if command_list is None:
        command_list = []
        command_paths\
            = [command_path] if command_path else \
            itertools.chain([_default_command_path],  # Built-in commands
                            spack.extensions.get_command_paths())  # Extensions
        for path in command_paths:
            for file in os.listdir(path):
                if file.endswith(".py") and not re.search(ignore_files, file):
                    cmd = re.sub(r'.py$', '', file)
                    command_list.append(cmd_name(cmd))

        command_list.sort()

    return command_list


def remove_options(parser, *options):
    """Remove some options from a parser."""
    for option in options:
        for action in parser._actions:
            if vars(action)['option_strings'][0] == option:
                parser._handle_conflict_resolve(None, [(option, action)])
                break


def get_module_from(cmd_name, namespace):
    """Imports the module for a particular command from the specified namespace.

    Args:
        cmd_name (str): name of the command for which to get a module
            (contains ``-``, not ``_``).
        namespace (str): namespace for command.
    """
    pname = python_name(cmd_name)

    module_name = '{0}.cmd.{1}'.format(namespace, pname)
    module = __import__(module_name,
                        fromlist=[pname, SETUP_PARSER, DESCRIPTION],
                        level=0)
    tty.debug('Imported command {0} as {1}.cmd.{2}'.
              format(cmd_name, namespace, pname))

    attr_setdefault(module, SETUP_PARSER, lambda *args: None)  # null-op
    attr_setdefault(module, DESCRIPTION, "")

    if not hasattr(module, pname):
        tty.die("Command module %s (%s) must define function '%s'." %
                (module.__name__, module.__file__, pname))
    return module


def get_module(cmd_name):
    """Imports the module for a particular Spack or extension top-level
    command name and returns it.

    Args:
        cmd_name (str): name of the command for which to get a module
            (contains ``-``, not ``_``).
    """
    try:
        module = get_module_from(cmd_name, 'spack')
    except ImportError:
        module = spack.extensions.get_module(cmd_name)

    return module


def get_command(cmd_name):
    """Imports a top level command's function from a module and returns it.

    Args:
        cmd_name (str): name of the command for which to get a module
            (contains ``-``, not ``_``).
    """
    pname = python_name(cmd_name)
    return getattr(get_module(cmd_name), pname)


def parse_specs(args, **kwargs):
    """Convenience function for parsing arguments from specs.  Handles common
       exceptions and dies if there are errors.
    """
    concretize = kwargs.get('concretize', False)
    normalize = kwargs.get('normalize', False)
    tests = kwargs.get('tests', False)

    try:
        specs = spack.spec.parse(args)
        for spec in specs:
            if concretize:
                spec.concretize(tests=tests)  # implies normalize
            elif normalize:
                spec.normalize(tests=tests)

        return specs

    except spack.spec.SpecParseError as e:
        msg = e.message + "\n" + str(e.string) + "\n"
        msg += (e.pos + 2) * " " + "^"
        raise SpackError(msg)

    except spack.spec.SpecError as e:

        msg = e.message
        if e.long_message:
            msg += e.long_message

        raise SpackError(msg)


def elide_list(line_list, max_num=10):
    """Takes a long list and limits it to a smaller number of elements,
       replacing intervening elements with '...'.  For example::

           elide_list([1,2,3,4,5,6], 4)

       gives::

           [1, 2, 3, '...', 6]
    """
    if len(line_list) > max_num:
        return line_list[:max_num - 1] + ['...'] + line_list[-1:]
    else:
        return line_list


def disambiguate_spec(spec, env):
    """Given a spec, figure out which installed package it refers to.

    Arguments:
        spec (spack.spec.Spec): a spec to disambiguate
        env (spack.environment.Environment): a spack environment,
            if one is active, or None if no environment is active
    """
    hashes = env.all_hashes() if env else None
    matching_specs = spack.store.db.query(spec, hashes=hashes)
    if not matching_specs:
        tty.die("Spec '%s' matches no installed packages." % spec)

    elif len(matching_specs) > 1:
        args = ["%s matches multiple packages." % spec,
                "Matching packages:"]
        args += [colorize("  @K{%s} " % s.dag_hash(7)) +
                 s.cformat('$_$@$%@$=') for s in matching_specs]
        args += ["Use a more specific spec."]
        tty.die(*args)

    return matching_specs[0]


def gray_hash(spec, length):
    h = spec.dag_hash(length) if spec.concrete else '-' * length
    return colorize('@K{%s}' % h)


def display_specs(specs, args=None, **kwargs):
    """Display human readable specs with customizable formatting.

    Prints the supplied specs to the screen, formatted according to the
    arguments provided.

    Specs are grouped by architecture and compiler, and columnized if
    possible.  There are three possible "modes":

      * ``short`` (default): short specs with name and version, columnized
      * ``paths``: Two columns: one for specs, one for paths
      * ``deps``: Dependency-tree style, like ``spack spec``; can get long

    Options can add more information to the default display. Options can
    be provided either as keyword arguments or as an argparse namespace.
    Keyword arguments take precedence over settings in the argparse
    namespace.

    Args:
        specs (list of spack.spec.Spec): the specs to display
        args (optional argparse.Namespace): namespace containing
            formatting arguments

    Keyword Args:
        mode (str): Either 'short', 'paths', or 'deps'
        long (bool): Display short hashes with specs
        very_long (bool): Display full hashes with specs (supersedes ``long``)
        namespace (bool): Print namespaces along with names
        show_flags (bool): Show compiler flags with specs
        variants (bool): Show variants with specs
        indent (int): indent each line this much
        decorators (dict): dictionary mappng specs to decorators
        header_callback (function): called at start of arch/compiler sections
        all_headers (bool): show headers even when arch/compiler aren't defined
    """
    def get_arg(name, default=None):
        """Prefer kwargs, then args, then default."""
        if name in kwargs:
            return kwargs.get(name)
        elif args is not None:
            return getattr(args, name, default)
        else:
            return default

    mode          = get_arg('mode', 'short')
    hashes        = get_arg('long', False)
    namespace     = get_arg('namespace', False)
    flags         = get_arg('show_flags', False)
    full_compiler = get_arg('show_full_compiler', False)
    variants      = get_arg('variants', False)
    all_headers   = get_arg('all_headers', False)

    decorator     = get_arg('decorator', None)
    if decorator is None:
        decorator = lambda s, f: f

    indent = get_arg('indent', 0)
    ispace = indent * ' '

    hlen = 7
    if get_arg('very_long', False):
        hashes = True
        hlen = None

    nfmt = '{fullpackage}' if namespace else '{package}'
    ffmt = ''
    if full_compiler or flags:
        ffmt += '$%'
        if full_compiler:
            ffmt += '@'
        ffmt += '+'
    vfmt = '$+' if variants else ''
    format_string = '$%s$@%s%s' % (nfmt, ffmt, vfmt)

    # Make a dict with specs keyed by architecture and compiler.
    index = index_by(specs, ('architecture', 'compiler'))
    transform = {'package': decorator, 'fullpackage': decorator}

    # Traverse the index and print out each package
    for i, (architecture, compiler) in enumerate(sorted(index)):
        if i > 0:
            print()

        header = "%s{%s} / %s{%s}" % (
            spack.spec.architecture_color,
            architecture if architecture else 'no arch',
            spack.spec.compiler_color,
            compiler if compiler else 'no compiler')

        # Sometimes we want to display specs that are not yet concretized.
        # If they don't have a compiler / architecture attached to them,
        # then skip the header
        if all_headers or (architecture is not None or compiler is not None):
            sys.stdout.write(ispace)
            tty.hline(colorize(header), char='-')

        specs = index[(architecture, compiler)]
        specs.sort()

        if mode == 'paths':
            # Print one spec per line along with prefix path
            abbreviated = [s.cformat(format_string, transform=transform)
                           for s in specs]
            width = max(len(s) for s in abbreviated)
            width += 2

            for abbrv, spec in zip(abbreviated, specs):
                # optional hash prefix for paths
                h = gray_hash(spec, hlen) if hashes else ''

                # only show prefix for concrete specs
                prefix = spec.prefix if spec.concrete else ''

                # print it all out at once
                fmt = "%%s%%s    %%-%ds%%s" % width
                print(fmt % (ispace, h, abbrv, prefix))

        elif mode == 'deps':
            for spec in specs:
                print(spec.tree(
                    format=format_string,
                    indent=4,
                    prefix=(lambda s: gray_hash(s, hlen)) if hashes else None))

        elif mode == 'short':
            def fmt(s):
                string = ""
                if hashes:
                    string += gray_hash(s, hlen) + ' '
                string += s.cformat(
                    '$%s$@%s' % (nfmt, vfmt), transform=transform)
                return string

            if not flags and not full_compiler:
                # Print columns of output if not printing flags
                colify((fmt(s) for s in specs), indent=indent)

            else:
                # Print one entry per line if including flags
                for spec in specs:
                    # Print the hash if necessary
                    hsh = gray_hash(spec, hlen) + ' ' if hashes else ''
                    print(ispace + hsh + spec.cformat(
                        format_string, transform=transform))

        else:
            raise ValueError(
                "Invalid mode for display_specs: %s. Must be one of (paths,"
                "deps, short)." % mode)


def spack_is_git_repo():
    """Ensure that this instance of Spack is a git clone."""
    with working_dir(spack.paths.prefix):
        return os.path.isdir('.git')


########################################
# argparse types for argument validation
########################################
def extant_file(f):
    """
    Argparse type for files that exist.
    """
    if not os.path.isfile(f):
        raise argparse.ArgumentTypeError('%s does not exist' % f)
    return f

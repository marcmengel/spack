# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
"""Service functions and classes to implement the hooks
for Spack's command extensions.
"""
import os
import re
import sys

import llnl.util.lang
import llnl.util.tty as tty

import spack.config
import spack.cmd
from spack.error import SpackError


_command_paths = []
_extension_regexp = re.compile(r'spack-([\w]*)')
_extension_command_map = None


class CommandNotFoundError(SpackError):
    """Exception class thrown when a requested command is not recognized as
    such.
    """
    def __init__(self, cmd_name):
        super(CommandNotFoundError, self).__init__(
            '{0} is not a recognized Spack command or extension command.'
            .format(cmd_name),
            'Known commands: {0}'.format(' '.join(spack.cmd.all_commands())))


def extension_name(path):
    """Returns the name of the extension in the path passed as argument.

    Args:
        path (str): path where the extension resides

    Returns:
        The extension name or None if path doesn't match the format
        for Spack's extension.
    """
    regexp_match = re.search(_extension_regexp, os.path.basename(path))
    if not regexp_match:
        msg = "[FOLDER NAMING]"
        msg += " {0} doesn't match the format for Spack's extensions"
        tty.warn(msg.format(path))
        return None
    return regexp_match.group(1)


def get_command_paths():
    _init_extension_command_map()  # Ensure we are initialized.
    return _command_paths


def _init_extension_command_map():
    """Return the list of paths where to search for command files."""
    global _extension_command_map
    if _extension_command_map is None:
        _extension_command_map = {}
        extension_paths = spack.config.get('config:extensions') or []
        sys.path.extend(extension_paths)
        for path in extension_paths:
            extension = extension_name(path)
            if extension:
                command_path = os.path.join(path, extension, 'cmd')
                _command_paths.append(command_path)
                commands = spack.cmd.find_commands(command_path)
                _extension_command_map.update(
                    dict((command, path) for command in
                         commands if command not in _extension_command_map))


def load_command_extension(command):
    """Loads a command extension from the path passed as argument.

    Args:
        command (str): name of the command

    Returns:
        A valid module object if the command is found or None
    """
    _init_extension_command_map()  # Ensure we have initialized.
    global _extension_command_map
    if command in _extension_command_map:
        # Decide if we're going to attempt to load the command extension
        # with __import__ or as a file.
        path = _extension_command_map[command]
        extension = extension_name(path)
        command_path = os.path.join(path, extension, 'cmd')
        if os.path.exists(os.path.join(command_path, '__init__.py')):
            # Import.
            module = spack.cmd.get_module_from(command, extension)
        else:
            # File.
            command_pname = spack.cmd.python_name(command)
            module_name = '{0}.{1}'.format(__name__, command_pname)
            command_filepath = os.path.join(command_path, command + '.py')
            module = llnl.util.lang.load_module_from_file(module_name,
                                                          command_filepath)
    else:
        raise CommandNotFoundError(command)
    return module


def path_for_extension(target_name, *paths):
    """Return the test root dir for a given extension.

    Args:
        target_name (str): name of the extension to test
        *paths: paths where the extensions reside

    Returns:
        Root directory where tests should reside or None
    """
    for path in paths:
        name = extension_name(path)
        if name == target_name:
            return path
    else:
        raise IOError('extension "{0}" not found'.format(target_name))


def get_template_dirs():
    """Returns the list of directories where to search for templates
    in extensions.
    """
    extension_dirs = spack.config.get('config:extensions') or []
    extensions = [os.path.join(x, 'templates') for x in extension_dirs]
    return extensions

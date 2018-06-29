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
"""Service functions and classes to implement the hooks
for Spack's command extensions.
"""
import os
import re

import llnl.util.lang
import llnl.util.tty as tty

extension_regexp = re.compile(r'spack-([\w]*)')


def extension_name(path):
    """Returns the name of the extension in the path passed as argument.

    Args:
        path (str): path where the extension resides

    Returns:
        The extension name or None if path doesn't match the format
        for Spack's extension.
    """
    regexp_match = re.search(extension_regexp, os.path.basename(path))
    if not regexp_match:
        msg = "[FOLDER NAMING]"
        msg += " {0} doesn't match the format for Spack's extensions"
        tty.warn(msg.format(path))
        return None
    return regexp_match.group(1)


def load_command_extension(command, path):
    """Loads a command extension from the path passed as argument.

    Args:
        command (str): name of the command
        path (str): base path of the command extension

    Returns:
        A valid module object if the command is found or None
    """
    extension = extension_name(path)
    if not extension:
        return None

    # Compute the absolute path of the file to be loaded, along with the
    # name of the python module where it will be stored
    cmd_path = os.path.join(path, extension, 'cmd', command + '.py')
    python_name = command.replace('-', '_')
    module_name = '{0}.{1}'.format(__name__, python_name)

    try:
        module = llnl.util.lang.load_module_from_file(module_name, cmd_path)
    except (ImportError, IOError):
        module = None

    return module


def command_paths(*paths):
    """Generator that yields paths where to search for command files.

    Args:
        *paths: paths where the extensions reside

    Returns:
        Paths where to search for command files.
    """
    for path in paths:
        extension = extension_name(path)
        if extension:
            yield os.path.join(path, extension, 'cmd')

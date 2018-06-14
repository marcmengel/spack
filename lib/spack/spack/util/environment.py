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
import os
import itertools
from six import iteritems
from operator import itemgetter
# TODO: This would be easier if we could import builtins in Python2.
try:
    from itertools import izip as iterzip
except ImportError:
    iterzip = zip

system_paths = ['/', '/usr', '/usr/local']
suffixes = ['bin', 'bin64', 'include', 'lib', 'lib64']
system_dirs = [os.path.join(p, s) for s in suffixes for p in system_paths] + \
    system_paths


def is_system_path(path):
    """Predicate that given a path returns True if it is a system path,
    False otherwise.

    Args:
        path (str): path to a directory

    Returns:
        True or False
    """
    return os.path.normpath(path) in system_dirs


def filter_system_paths(paths):
    """Return only paths that are not system paths."""
    return [p for p in paths if not is_system_path(p)]


def system_paths(paths):
    """Return only paths that are system paths."""
    return [p for p in paths if is_system_path(p)]


def deprioritize_system_paths(paths):
    """Put system paths at the end of paths, otherwise preserving order."""
    return filter_system_paths(paths) + system_paths(paths)


def prune_duplicate_paths(paths):
    """Returns the paths with duplicates removed, order preserved."""
    return [key for key, value in
            sorted(iteritems(dict(iterzip(reversed(paths),
                                          itertools.count(0, -1)))),
                   key=itemgetter(1))]


def get_path(name):
    path = os.environ.get(name, "").strip()
    if path:
        return path.split(":")
    else:
        return []


def env_flag(name):
    if name in os.environ:
        value = os.environ[name].lower()
        return value == "true" or value == "1"
    return False


def path_set(var_name, directories):
    path_str = ":".join(str(dir) for dir in directories)
    os.environ[var_name] = path_str


def path_put_first(var_name, directories):
    """Puts the provided directories first in the path, adding them
       if they're not already there.
    """
    path = os.environ.get(var_name, "").split(':')

    for dir in directories:
        if dir in path:
            path.remove(dir)

    new_path = tuple(directories) + tuple(path)
    path_set(var_name, new_path)


def dump_environment(path):
    """Dump the current environment out to a file."""
    with open(path, 'w') as env_file:
        for key, val in sorted(os.environ.items()):
            env_file.write('export %s="%s"\n' % (key, val))

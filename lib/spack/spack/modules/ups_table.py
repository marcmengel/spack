# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

"""This module implements the classes necessary to generate TCL
non-hierarchical modules.
"""
import os.path
import string
import inspect

import llnl.util.tty as tty

import spack.config
import spack.tengine as tengine
from .common import BaseConfiguration, BaseFileLayout
from .common import BaseContext, BaseModuleFileWriter
from .common import root_path

#: TCL specific part of the configuration
configuration = spack.config.get('modules:ups_table', {})

#: Caches the configuration {spec_hash: configuration}
configuration_registry = {}


def make_configuration(spec):
    """Returns the ups_table configuration for spec"""
    key = spec.dag_hash()
    try:
        return configuration_registry[key]
    except KeyError:
        return configuration_registry.setdefault(key, UpsTableConfiguration(spec))


def make_layout(spec):
    """Returns the layout information for spec """
    conf = make_configuration(spec)
    return UpsTableFileLayout(conf)


def make_context(spec):
    """Returns the context information for spec"""
    conf = make_configuration(spec)
    return UpsTableContext(conf)


class UpsTableConfiguration(BaseConfiguration):
    """Configuration class for ups_table module files."""

    @property
    def conflicts(self):
        """Conflicts for this module file"""
        return self.conf.get('conflict', [])


class UpsTableFileLayout(BaseFileLayout):
    """File layout for ups_table module files."""

    extension = "table"

    def dirname(self):
        return root_path('ups_table') + '/'+ self.spec.format("{name}")

    @property
    def filename(self):
        """Name of the module file for the current spec."""
        fn = self.spec.format("{name}_{version}.table")
        fp = os.path.join(self.dirname(), fn)
        return  fp

class UpsTableContext(BaseContext):
    """Context class for ups_table module files."""

    @tengine.context_property
    def prerequisites(self):
        """List of modules that needs to be loaded automatically."""
        return self._create_module_list_of('specs_to_prereq')

    @tengine.context_property
    def conflicts(self):
        """List of conflicts for the ups_table module file."""
        fmts = []
        naming_scheme = self.conf.naming_scheme
        f = string.Formatter()
        for item in self.conf.conflicts:
            if len([x for x in f.parse(item)]) > 1:
                for naming_dir, conflict_dir in zip(
                        naming_scheme.split('/'), item.split('/')
                ):
                    if naming_dir != conflict_dir:
                        message = 'conflict scheme does not match naming '
                        message += 'scheme [{spec}]\n\n'
                        message += 'naming scheme   : "{nformat}"\n'
                        message += 'conflict scheme : "{cformat}"\n\n'
                        message += '** You may want to check your '
                        message += '`modules.yaml` configuration file **\n'
                        tty.error(message.format(spec=self.spec,
                                                 nformat=naming_scheme,
                                                 cformat=item))
                        raise SystemExit('Module generation aborted.')
                item = self.spec.format(item)
            fmts.append(item)
        # Substitute spec tokens if present
        return [self.spec.format(x) for x in fmts]


class UpsTableModulefileWriter(BaseModuleFileWriter):
    """Writer class for ups_table module files."""
    default_template = os.path.join('modules', 'modulefile.ups_table')

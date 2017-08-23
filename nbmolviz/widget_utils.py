# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from future import standard_library

standard_library.install_aliases()
# Copyright 2017 Autodesk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import collections


def can_use_widgets():
    """ Expanded from from http://stackoverflow.com/a/34092072/1958900
    """
    if 'IPython' not in sys.modules:
        # IPython hasn't been imported, definitely not
        return False
    from IPython import get_ipython

    # check for `kernel` attribute on the IPython instance
    if getattr(get_ipython(), 'kernel', None) is None:
        return False

    try:
        import ipywidgets as ipy
        import traitlets
    except ImportError:
        return False

    if int(ipy.__version__.split('.')[0]) < 6:
        print('WARNING: widgets require ipywidgets 6.0 or later')
        return False

    return True

EXTENSION_DEPS = ['widgetsnbextension', 'nbmolviz']


def extensions_install_check():
    from .install import get_installed_versions

    versions = collections.OrderedDict(
            (dep, get_installed_versions(dep, dep == 'nbmolviz'))
            for dep in EXTENSION_DEPS)
    state = {dep: {'installed': False, 'enabled': False} for dep in EXTENSION_DEPS}

    for dep in EXTENSION_DEPS:
        for location, version in versions[dep].items():
            if not state[dep]['installed'] and version.installed:
                state[dep]['installed'] = location
                state[dep]['version'] = version.version

            if not state[dep]['enabled'] and version.enabled:
                state[dep]['enabled'] = location

    return state


def print_extension_warnings():
    from . import install
    state = extensions_install_check()
    preferred_loc = install.preferred_install_location()
    warnings = []

    for dep in ['widgetsnbextension', 'nbmolviz']:
        installed = state[dep]['installed']
        enabled = state[dep]['enabled']

        if not installed:
            warnings.append('- the "{dep}" notebook extension is not installed. To install it, run:'
                            '\n   $ jupyter nbextension install {dep} --python {flag}'
                            .format(dep=dep, flag=install.FLAGS[preferred_loc]))

        if not enabled:
            if installed:
                flag = install.FLAGS[installed]
                warnings.append(
                        '- the "{dep}" notebook extension is not enabled. '
                        'To enable it, run:'.format(dep=dep))
            else:
                flag = install.FLAGS[preferred_loc]

            warnings[-1] += ('\n   $ jupyter nbextension enable {dep} --python {flag}'
                             .format(dep=dep, flag=flag))

    if state['widgetsnbextension']['installed'] and state['widgetsnbextension']['enabled']:
        warnings.append('You can also perform these tasks using `moldesign.configure()`')

    if warnings:
        print('WARNING: notebook visualizations are currently disabled because:\n')
        print('\n\n'.join(warnings))
        print('\nSave your notebook and reload the page after making these changes.')


def extension_version_check():
    from .install import get_installed_versions
    versions = get_installed_versions('nbmolviz', True)

    active = None
    for loc, vers in versions.items():
        if vers.active:
            active = vers
            break

    if active is None:
        raise ValueError("No extensions are active")






LAYOUT_PROPS = set(("height width max_height max_width min_height min_width "
                    "visibility display overflow overflow_x overflow_y  border margin "
                    "padding top left bottom right order flex_flow align_items "
                    "flex align_self align_content justify_content").split())


def process_widget_kwargs(kwargs):
    from ipywidgets import Layout

    layout = kwargs.get('layout', None)

    for arg in list(kwargs.keys()):
        if arg in LAYOUT_PROPS:
            if not layout:
                layout = Layout()
            setattr(layout, arg, kwargs.pop(arg))

    if layout is not None:
        kwargs['layout'] = layout

    return kwargs

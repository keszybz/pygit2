# -*- coding: UTF-8 -*-
# coding: UTF-8
#
# Copyright 2010 Google, Inc.
# Copyright 2011 Itaapy
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

"""Setup file for pygit2."""

import os
import sys
import logging
from distutils.core import setup, Extension, Command
from distutils.command.build import build

# Use environment variable LIBGIT2 to set your own libgit2 configuration.
libgit2_path = os.getenv("LIBGIT2")
if libgit2_path is None:
    if os.name == 'nt':
        program_files = os.getenv("ProgramFiles")
        libgit2_path = '%s\libgit2' % program_files
    else:
        libgit2_path = '/usr/local'

libgit2_bin = os.path.join(libgit2_path, 'bin')
libgit2_include = os.path.join(libgit2_path, 'include')
libgit2_lib =  os.path.join(libgit2_path, 'lib')

class TestCommand(Command):
    """Command for running pygit2 tests."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build')
        bld = self.distribution.get_command_obj('build')
        sys.path = [os.path.abspath(bld.build_lib)] + sys.path
        import test
        test.main()


class BuildWithDLLs(build):

    # On Windows, we install the git2.dll too.
    def _get_dlls(self):
        # return a list of of (FQ-in-name, relative-out-name) tuples.
        ret = []
        bld_ext = self.distribution.get_command_obj('build_ext')
        compiler_type = bld_ext.compiler.compiler_type
        libgit2_dlls = []
        if compiler_type == 'msvc':
            libgit2_dlls.append('git2.dll')
        elif compiler_type == 'mingw32':
            libgit2_dlls.append('libgit2.dll')
        look_dirs = [libgit2_bin] + os.environ.get("PATH","").split(os.pathsep)
        target = os.path.abspath(self.build_lib)
        for bin in libgit2_dlls:
            for look in look_dirs:
                f = os.path.join(look, bin)
                if os.path.isfile(f):
                    ret.append((f, target))
                    break
            else:
                logging.warning("Could not find required DLL %r to copy, (looked in %s)",
                    bin, look_dirs)
        return ret

    def run(self):
        build.run(self)
        if os.name == 'nt':
            # On Windows we package up the dlls with the plugin.
            for s, d in self._get_dlls():
                self.copy_file(s, d)


kwargs = {'cmdclass': {'test': TestCommand, 'build': BuildWithDLLs}}


classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Version Control"]


with open('README.rst') as readme:
    long_description = readme.read()

setup(name='pygit2',
      description='Python bindings for libgit2.',
      keywords='git',
      version='0.16.1',
      url='http://github.com/libgit2/pygit2',
      classifiers=classifiers,
      license='GPLv2',
      maintainer='J. David Ibáñez',
      maintainer_email='jdavid.ibp@gmail.com',
      long_description=long_description,
      ext_modules=[
          Extension('pygit2', ['pygit2.c'],
                    include_dirs=[libgit2_include],
                    library_dirs=[libgit2_lib],
                    libraries=['git2']),
          ],
      **kwargs)

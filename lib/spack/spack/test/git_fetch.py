# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import copy
import os
import shutil

import pytest

from llnl.util.filesystem import working_dir, touch, mkdirp

import spack.repo
import spack.config
from spack.spec import Spec
from spack.stage import Stage
from spack.version import ver
from spack.fetch_strategy import GitFetchStrategy
from spack.util.executable import which


pytestmark = pytest.mark.skipif(
    not which('git'), reason='requires git to be installed')


_mock_transport_error = 'Mock HTTP transport error'


@pytest.fixture(params=[None, '1.8.5.2', '1.8.5.1', '1.7.10', '1.7.0'])
def git_version(request, monkeypatch):
    """Tests GitFetchStrategy behavior for different git versions.

    GitFetchStrategy tries to optimize using features of newer git
    versions, but needs to work with older git versions.  To ensure code
    paths for old versions still work, we fake it out here and make it
    use the backward-compatibility code paths with newer git versions.
    """
    git = which('git', required=True)
    real_git_version = ver(git('--version', output=str).lstrip('git version '))

    if request.param is None:
        yield    # don't patch; run with the real git_version method.
    else:
        test_git_version = ver(request.param)
        if test_git_version > real_git_version:
            pytest.skip("Can't test clone logic for newer version of git.")

        # Patch the fetch strategy to think it's using a lower git version.
        # we use this to test what we'd need to do with older git versions
        # using a newer git installation.
        monkeypatch.setattr(GitFetchStrategy, 'git_version', test_git_version)
        yield


@pytest.fixture
def mock_bad_git(monkeypatch):
    """
    Test GitFetchStrategy behavior with a bad git command for git >= 1.7.1
    to trigger a SpackError.
    """
    def bad_git(*args, **kwargs):
        """Raise a SpackError with the transport message."""
        raise spack.error.SpackError(_mock_transport_error)

    # Patch the fetch strategy to think it's using a git version that
    # will error out when git is called.
    monkeypatch.setattr(GitFetchStrategy, 'git', bad_git)
    monkeypatch.setattr(GitFetchStrategy, 'git_version', ver('1.7.1'))
    yield


def test_bad_git(tmpdir, mock_bad_git):
    """Trigger a SpackError when attempt a fetch with a bad git."""
    testpath = str(tmpdir)

    with pytest.raises(spack.error.SpackError):
        fetcher = GitFetchStrategy(git='file:///not-a-real-git-repo')
        with Stage(fetcher, path=testpath):
            fetcher.fetch()


@pytest.mark.parametrize("type_of_test", ['master', 'branch', 'tag', 'commit'])
@pytest.mark.parametrize("secure", [True, False])
def test_fetch(type_of_test,
               secure,
               mock_git_repository,
               config,
               mutable_mock_packages,
               git_version):
    """Tries to:

    1. Fetch the repo using a fetch strategy constructed with
       supplied args (they depend on type_of_test).
    2. Check if the test_file is in the checked out repository.
    3. Assert that the repository is at the revision supplied.
    4. Add and remove some files, then reset the repo, and
       ensure it's all there again.
    """
    # Retrieve the right test parameters
    t = mock_git_repository.checks[type_of_test]
    h = mock_git_repository.hash

    # Construct the package under test
    spec = Spec('git-test')
    spec.concretize()
    pkg = spack.repo.get(spec)
    pkg.versions[ver('git')] = t.args

    # Enter the stage directory and check some properties
    with pkg.stage:
        with spack.config.override('config:verify_ssl', secure):
            pkg.do_stage()

        with working_dir(pkg.stage.source_path):
            assert h('HEAD') == h(t.revision)

            file_path = os.path.join(pkg.stage.source_path, t.file)
            assert os.path.isdir(pkg.stage.source_path)
            assert os.path.isfile(file_path)

            os.unlink(file_path)
            assert not os.path.isfile(file_path)

            untracked_file = 'foobarbaz'
            touch(untracked_file)
            assert os.path.isfile(untracked_file)
            pkg.do_restage()
            assert not os.path.isfile(untracked_file)

            assert os.path.isdir(pkg.stage.source_path)
            assert os.path.isfile(file_path)

            assert h('HEAD') == h(t.revision)


@pytest.mark.parametrize("type_of_test", ['branch', 'commit'])
def test_debug_fetch(type_of_test, mock_git_repository, config):
    """Fetch the repo with debug enabled."""
    # Retrieve the right test parameters
    t = mock_git_repository.checks[type_of_test]

    # Construct the package under test
    spec = Spec('git-test')
    spec.concretize()
    pkg = spack.repo.get(spec)
    pkg.versions[ver('git')] = t.args

    # Fetch then ensure source path exists
    with pkg.stage:
        with spack.config.override('config:debug', True):
            pkg.do_fetch()
            assert os.path.isdir(pkg.stage.source_path)


def test_git_extra_fetch(tmpdir):
    """Ensure a fetch after 'expanding' is effectively a no-op."""
    testpath = str(tmpdir)

    fetcher = GitFetchStrategy(git='file:///not-a-real-git-repo')
    with Stage(fetcher, path=testpath) as stage:
        mkdirp(stage.source_path)
        fetcher.fetch()   # Use fetcher to fetch for code coverage
        shutil.rmtree(stage.source_path)


def test_needs_stage():
    """Trigger a NoStageError when attempt a fetch without a stage."""
    with pytest.raises(spack.fetch_strategy.NoStageError,
                       matches=_mock_transport_error):
        fetcher = GitFetchStrategy(git='file:///not-a-real-git-repo')
        fetcher.fetch()


@pytest.mark.parametrize("all_branches", [True, False])
def test_all_branches(all_branches, mock_git_repository,
                      config, mutable_mock_packages):
    """Ensure that we can force all branches to be downloaded."""

    git_version\
        = ver(mock_git_repository.git_exe('--version', output=str).
              lstrip('git version '))
    if git_version < ver('1.7.10'):
        pytest.skip('Not testing --single-branch for older git')

    secure = True
    type_of_test = 'tag-branch'

    t = mock_git_repository.checks[type_of_test]

    spec = Spec('git-test')
    spec.concretize()
    pkg = spack.repo.get(spec)

    args = copy.copy(t.args)
    args['all_branches'] = all_branches
    pkg.versions[ver('git')] = args

    with pkg.stage:
        with spack.config.override('config:verify_ssl', secure):
            pkg.do_stage()
            with working_dir(pkg.stage.source_path):
                branches\
                    = mock_git_repository.git_exe('branch', '-a',
                                                  output=str).splitlines()
        nbranches = len(branches)
        if all_branches:
            assert(nbranches == 5)
        else:
            assert(nbranches == 2)


@pytest.mark.parametrize("full_depth", [True, False])
def test_full_depth(full_depth, mock_git_repository,
                    config, mutable_mock_packages):
    """Ensure that we can clone a repository at full depth."""

    git_version\
        = ver(mock_git_repository.git_exe('--version', output=str).
              lstrip('git version '))
    if git_version < ver('1.7.1'):
        pytest.skip('Not testing --depth for older git')

    secure = True
    type_of_test = 'tag-branch'

    t = mock_git_repository.checks[type_of_test]

    spec = Spec('git-test')
    spec.concretize()
    pkg = spack.repo.get(spec)
    args = copy.copy(t.args)
    args['full_depth'] = full_depth
    pkg.versions[ver('git')] = args

    with pkg.stage:
        with spack.config.override('config:verify_ssl', secure):
            pkg.do_stage()
            with working_dir(pkg.stage.source_path):
                commits\
                    = mock_git_repository.\
                    git_exe('log', '--graph',
                            '--pretty=format:%h -%d %s (%ci) <%an>',
                            '--abbrev-commit',
                            output=str).splitlines()
                ncommits = len(commits)
        if full_depth:
            assert(ncommits == 2)
        else:
            assert(ncommits == 1)

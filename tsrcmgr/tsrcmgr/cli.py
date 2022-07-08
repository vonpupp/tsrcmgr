#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.

It can be used as a handy facility for running the task from a command line.

.. note::

    To learn more about Click visit the
    `project website <http://click.pocoo.org/5/>`_.  There is also a very
    helpful `tutorial video <https://www.youtube.com/watch?v=kNke39OZ2k0>`_.

    To learn more about running Luigi, visit the Luigi project's
    `Read-The-Docs <http://luigi.readthedocs.io/en/stable/>`_ page.

.. currentmodule:: tsrcmgr.cli
.. moduleauthor:: vonpupp <vonpupp@gmail.com>
"""
import click
import dictdiffer
import logging
import os
import yaml
from .__init__ import __version__
from collections import OrderedDict

DEFAULT_INPUT_FILE = os.path.expanduser('~/.tsrcmgr/metamanifest.yml')

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}  #: a mapping of `verbose` option counts to logging levels


class Info(object):
    """An information object to pass data between CLI functions."""

    def __init__(self):  # Note: This object must have an empty constructor.
        """Create a new instance."""
        self.verbose: int = 0


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(Info, ensure=True)


class UnsortableList(list):
    """This should work as an unsortable list but it not working as intended."""

    def sort(self, *args, **kwargs):
        """Override de sort method"""
        pass


class UnsortableOrderedDict(OrderedDict):
    """This should work as an unsortable dict but it not working as intended."""

    def items(self, *args, **kwargs):
        """Override de items method"""
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))


yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)


# Change the options to below to suit the actual options for your task (or
# tasks).
@click.group()
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
@pass_info
def cli(info: Info, verbose: int):
    """Run tsrcmgr."""
    # Use the verbosity count to determine the logging level...
    if verbose > 0:
        logging.basicConfig(
            level=LOGGING_LEVELS[verbose]
            if verbose in LOGGING_LEVELS
            else logging.DEBUG
        )
        click.echo(
            click.style(
                f"Verbose logging is enabled. "
                f"(LEVEL={logging.getLogger().getEffectiveLevel()})",
                fg="yellow",
            )
        )
    info.verbose = verbose


def apply_remotes(repo, remotes_list, org_name, repo_name):
    """Apply the remote patterns from the metamanifest file"""
    for remote in remotes_list:
        remote_out = UnsortableOrderedDict()
        remote_name = remote['remote-name']
        remote_url = remote['url-format']
        remote_out['name'] = remote_name
        remote_out['url'] = remote_url.format(org=org_name, repo=repo_name)
        repo['remotes'].append(remote_out)


@cli.command()
@pass_info
@click.option(
    '--input', '-i',
    type=click.File('rb'),
    default=DEFAULT_INPUT_FILE,
    help='Input file',
    show_default=True)
def gen(_: Info, input):
    """Generate the manifest.yml file."""
    config = yaml.safe_load(input)
    click.echo("Metamanifest loaded: {}".format(input.name))
    remote_remotes = config['remotes']
    local_remotes = config['locals']
    all_repos = []
    for mirror in config['mirrors']:
        repos = mirror['repos']
        output_json = UnsortableOrderedDict()
        output_json['repos'] = []
        output_fn = mirror['manifest-file']
        for fqdnrepo in repos:
            org = fqdnrepo.split('/')[0]
            repo = fqdnrepo.split('/')[1]
            try:
                branch = fqdnrepo.split('@')[1]
                repo = fqdnrepo.split('/')[1].split('@')[0]
            except Exception:
                branch = 'master'
            all_repos.append(repo)
            output_repo = UnsortableOrderedDict()
            output_repo['dest'] = repo
            output_repo['branch'] = branch
            output_repo['remotes'] = []
            apply_remotes(output_repo, remote_remotes, org, repo)
            apply_remotes(output_repo, local_remotes, org, repo)
            output_json['repos'].append(output_repo)

        output_json['groups'] = UnsortableOrderedDict()
        output_json['groups']['default'] = UnsortableOrderedDict()
        output_json['groups']['default']['repos'] = []
        output_json['groups']['default']['repos'] += all_repos
        fh = open(os.path.expanduser(output_fn), 'w')
        yaml.dump(output_json, fh)
        click.echo("Manifest written: {}".format(output_fn))


@cli.command()
@pass_info
@click.argument('file1', type=click.File('r'))
@click.argument('file2', type=click.File('r'))
def diff(_: Info, file1, file2):
    """Compare two manifests to see if they are equal."""
    data1_dict = yaml.load(file1, Loader=yaml.FullLoader)
    data2_dict = yaml.load(file2, Loader=yaml.FullLoader)

    if data1_dict == data2_dict:
        print("No difference detected")
    else:
        print("Differences detected:")
        for diff in list(dictdiffer.diff(data1_dict, data2_dict)):
            print(diff)


@cli.command()
def version():
    """Get the library version."""
    click.echo(click.style(f"{__version__}", bold=True))

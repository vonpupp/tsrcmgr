#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_cli
.. moduleauthor:: vonpupp <vonpupp@gmail.com>

This is the test module for the project's command-line interface (CLI)
module.
"""
# fmt: off
import tsrcmgr.cli as cli
from tsrcmgr import __version__
# fmt: on
from click.testing import CliRunner, Result


# To learn more about testing Click applications, visit the link below.
# http://click.pocoo.org/5/testing/


def test_version_displays_library_version():
    """
    Arrange/Act: Run the `version` subcommand.
    Assert: The output matches the library version.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["version"])
    assert (
        __version__ in result.output.strip()
    ), "Version number should match library version."


def test_verbose_output():
    """
    Arrange/Act: Run the `version` subcommand with the '-v' flag.
    Assert: The output indicates verbose logging is enabled.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["-v", "version"])
    assert (
        "Verbose" in result.output.strip()
    ), "Verbose logging should be indicated in output."


def test_gen():
    """
    Arrange/Act: Run the `version` subcommand.
    Assert:  The output matches the library version.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["gen", "--input", "test-assets/testinput.yml"])
    # fmt: off
    assert 'test-assets/testinput.yml' in result.output.strip(), \
        "Metamanifest loaded: test-assets/testinput.yml"

def test_diff():
    """
    Arrange/Act: Run the `version` subcommand.
    Assert:  The output matches the library version.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["diff", "test-assets/testoutput.yml", "test-assets/testoutput-diff.yml"])
    # fmt: off
    assert 'No difference detected' in result.output.strip(), \
        "No difference detected"

    # fmt: on

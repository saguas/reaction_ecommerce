from __future__ import unicode_literals, absolute_import
import click


click.disable_unicode_literals_warning = True


def call_command(cmd, context):
	return click.Context(cmd, obj=context).forward(cmd)

def get_commands():
	# prevent circular imports
	from .utils import commands as utils_commands
	from .site import commands as site_commands

	return list(set(utils_commands + site_commands))

commands = get_commands()
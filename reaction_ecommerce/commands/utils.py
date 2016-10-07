from __future__ import unicode_literals, absolute_import
import click
import frappe



@click.command('nginx')
def nginx():
    print "nginx command"





commands = [
	nginx,
]
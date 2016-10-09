#!/usr/bin/python
# -*- coding: latin-1 -*-

from __future__ import unicode_literals, absolute_import
import click
import frappe
from frappe.commands import pass_context



def get_admin_email():
	user = frappe.db.get("User", {"name": "Administrator"})
	return user.email

def update_password(sites, user_password, user_email):
	import getpass, os
	from frappe.utils.password import update_password as upd_pwd

	for site in sites:
		try:
			frappe.init(site=site)

			while not user_password:
				user_password = getpass.getpass("Administrator's password for {0}: ".format(site))

			while not user_email:
				user_email = raw_input("Administrator's email for {0}: ".format(site))
			# set password has meteor.js send to the server; as SHA256.
			from reaction_ecommerce.utils.users import hashpw
			frappe.connect()
			pwd_hash = hashpw(user_password)
			upd_pwd('Administrator', pwd_hash)
			frappe.db.commit()
			site_path = frappe.get_site_path()
			site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))
			site_config["admin_password"] = pwd_hash
			site_config["admin_email"] = user_email
			#write to file.
			with open(os.path.join(site_path, "site_config.json"), 'w') as txtfile:
				txtfile.write(frappe.as_json(site_config))
			user_password = None
		finally:
			frappe.destroy()



@click.command('set-admin-password')
@click.option('--admin-password')
@click.option('--admin-email')
@pass_context
def set_admin_password(context, admin_password, admin_email):
	"Set Administrator password for a site"
	update_password(context.sites, user_password=admin_password, user_email=admin_email)



commands = [
    set_admin_password
]
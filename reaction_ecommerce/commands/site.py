#!/usr/bin/python
# -*- coding: latin-1 -*-

from __future__ import unicode_literals, absolute_import
import click
import frappe, os
from frappe.commands import pass_context


def update_reaction_settings(admin_email, admin_password):
	reaction_setting_config = frappe._dict()
	# reaction_setting_config = frappe.get_file_json(os.path.join(common_config.get("meteor_app_path"), "settings", "dev.settings.json"))
	reaction_setting_config["ROOT_URL"] = ""
	reaction_setting_config["MONGO_URL"] = ""
	reaction_setting_config["FRAPPE_URL"] = "http://localhost"
	reaction_setting_config["DDP_DEFAULT_CONNECTION_URL"] = "http://localhost:3000/"
	reaction_setting_config["MAIL_URL"] = ""
	reaction_setting_config["reaction"] = {
		"REACTION_USER": "admin",
		"REACTION_AUTH": admin_password,
		"REACTION_EMAIL": admin_email,
	}
	reaction_setting_config["isDebug"] = "info"
	reaction_setting_config["public"] = {}
	reaction_setting_config["frappe"] = {
			"FRAPPE_ADMIN_USERNAME": "Administrator",
			"FRAPPE_URL": "http://localhost"
	}
	reaction_webapp_path = "../apps/reaction_ecommerce/reaction_ecommerce/www/webreaction"
	with open(os.path.join(reaction_webapp_path, "settings", "dev.settings.json"), 'w') as txtfile:
		txtfile.write(frappe.as_json(reaction_setting_config))


def set_admin_email(email):
	user = frappe.get_doc("User", {"name": "Administrator"})
	user.update({"email": email})
	user.save()

def get_admin_email():
	user = frappe.get_doc("User", {"name": "Administrator"})
	return user.email


def update_password(sites, user_password, user_email):
	import getpass
	from frappe.utils.password import update_password as upd_pwd

	for site in sites:
		try:
			frappe.init(site=site)

			while not user_password:
				user_password = getpass.getpass("Administrator's password for {0}: ".format(site))

			frappe.connect()
			default_email = get_admin_email()

			if not user_email:
				user_email = raw_input("Administrator's email for {0}, default email: ({1}) ".format(site, default_email))
			# set password has meteor.js send to the server; as SHA256.
			from reaction_ecommerce.utils.users import hashpw
			pwd_hash = hashpw(user_password)
			upd_pwd('Administrator', pwd_hash)
			site_path = frappe.get_site_path()
			site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))
			site_config["admin_password"] = pwd_hash
			site_config["admin_email"] = user_email or default_email
			if user_email and default_email != user_email:
				set_admin_email(user_email)

			frappe.db.commit()
			#write to file.
			with open(os.path.join(site_path, "site_config.json"), 'w') as txtfile:
				txtfile.write(frappe.as_json(site_config))

			update_reaction_settings(user_email or default_email, user_password)
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
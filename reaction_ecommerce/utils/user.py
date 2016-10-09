import frappe
import json


"""
# add user with some roles
# see frappe.utils.user function add_system_manager
def add_user(email, first_name=None, last_name=None, user_type="Website User",send_welcome_email=False):
	# add user
	# user_type: "System User" or "Website User"
	user = frappe.new_doc("User")
	user.update({
		"name": email,
		"email": email,
		"enabled": 1,
		"first_name": first_name or email,
		"last_name": last_name,
		"user_type": user_type,
		"send_welcome_email": 1 if send_welcome_email else 0
	})

	user.insert()

	# add roles
	roles = [""] #add here doctypes
	user.add_roles(*roles)

"""


# see frappe.client.insert
"""
frappe.client.insert

{"docstatus":0,"doctype":"User","name":"New User 1","__islocal":1,"__unsaved":1,"owner":"Administrator"
,"enabled":1,"send_welcome_email":0,"language":"pt","gender":"","thread_notify":1,"background_style"
:"Fill Screen","simultaneous_sessions":1,"user_type":"System User","__run_link_triggers":1,"email":"luisfmfernandes
@icloud.com","first_name":"Luis","last_name":"icloud"}

"""
@frappe.whitelist()
def insert_user(doc):
	if isinstance(doc, basestring):
		doc = json.loads(doc)

	# this is necessary because we have a hook in User inserts. If is_from_efrappe=True don't insert user in mongodb in User insert hook.
	frappe.local.flags.is_from_efrappe = True

	doc = frappe.get_doc(doc).insert()

	frappe.local.flags.is_from_efrappe = False

	return doc.as_dict()
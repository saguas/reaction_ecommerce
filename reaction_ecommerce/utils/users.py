import hashlib
import frappe
import bcrypt
import json


ROUNDS = 10
REACTIONDB = "meteor"


reaction_web_client = None


def hashpw(pwd):
	m = hashlib.sha256()
	m.update(pwd)
	hexpass = m.hexdigest()

	return hexpass


def bcrypt_hashpw(pwd):
	hexpass = hashpw(pwd)
	return bcrypt.hashpw(hexpass, bcrypt.gensalt(ROUNDS))


def pwd_compare(pwd, bcrypt_hash):
	return bcrypt.hashpw(pwd, bcrypt_hash)


def get_userId(email):
	client = get_mongo_client()
	db = client[REACTIONDB]
	users = db.users
	user = users.find_one({"emails.address": {"$in": [email]}})
	if user:
		return user._id
	return

def get_mongo_client():
	import reaction_ecommerce as rc
	return rc.get_mongo_cli()


def get_mongo_db():
	client = get_mongo_client()
	return client[REACTIONDB]

def get_mongo_user_password(username):
	db = get_mongo_db()
	users = db.users
	user = users.find_one({"emails.address":{"$in": [username]}})
	if user:
		return user.get("services").get("password").get("bcrypt")

	return None


def validate(doc, method=None):
	"""
		Validate users inserts and updates. Hash + bcrypt password for compatibility with reaction ecommerce app.
		Call reaction to create user in mongodb.
	"""
	if doc.get("__islocal"):#this is an insert
		return
	else:#this is an update. Check if password has changed
		from frappe.utils.password import check_password
		#userdoc = frappe.get_all("User", fields=["name", "password"], filters = {"name":doc.name})
		None
	return


def on_trash(doc, method=None):
	#remove from mongodb this user if not online
	None


def get_user_for_update_password(key, old_password):
	from frappe.core.doctype.user.user import _get_user_for_update_password

	res = _get_user_for_update_password(key, old_password)
	if res.get('message'):
		return None
	else:
		user = res['user']

	return user

@frappe.whitelist(allow_guest=True)
def update_password(new_password, key=None, old_password=None):
	from frappe.core.doctype.user.user import update_password as update_pwd

	print "in update_password form_dict: {}".format(frappe.local.form_dict)
	def user_callback(error, result):
		if error:
			print "error for creteFrappeUser {}".format(error)
		else:
			print "result for creteFrappeUser {}".format(result)

	orinal_new_pwd = new_password
	#orinal_old_pwd = old_password

	first_time = True

	if old_password:
		old_password = hashpw(old_password)
		first_time = False


	new_password = hashpw(new_password)

	url = update_pwd(new_password, key, old_password)

	if first_time and frappe.session.user != "Guest":
		#user has login
		#create user in reaction ecommerce
		import meteor_ddp as ddp
		user = get_user_for_update_password(key, old_password)
		if user:
			ddp.create_meteor_user(user.email, orinal_new_pwd, user.username, user_callback)
	elif frappe.session.user != "Guest":
		#change password
		import meteor_ddp as ddp

		user = get_user_for_update_password(key, old_password)
		if user:
			userId = get_userId(user.email)
			if userId:
				ddp.change_user_password(userId, orinal_new_pwd, user_callback)


	return url


@frappe.whitelist()
def verify_password(password):
	from frappe.core.doctype.user.user import verify_password as verify_pwd

	password = hashpw(password)
	return verify_pwd(password)


@frappe.whitelist(allow_guest=True)
def test_password_strength(new_password, key=None, old_password=None):
	from frappe.core.doctype.user.user import test_password_strength as test_pwd_strength

	if old_password:
		old_password = hashpw(old_password)

	new_password = hashpw(new_password)

	return test_pwd_strength(new_password, key, old_password)



def on_logout():
	print "on_logout {}".format(frappe.local.form_dict)
	if frappe.session.user == "Guest":
		print "user Guest, do nothing!!"
		return
	data = frappe.local.form_dict.data
	if data:
		obj = json.loads(data)
		if isinstance(obj, dict):
			origin = obj.get("efrappe").get("origin")
			if origin == "efrappe":
				return

	#logout from frappe desk
	db = get_mongo_db()
	email = frappe.session.user
	if email == "Administrator":
		user = frappe.get_doc("User", email)
		if user:
			email = user.email

	from frappe.auth import CookieManager
	from werkzeug.wrappers import Response
	response = Response()
	cookie_manager = CookieManager()

	cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])
	cookie_manager.flush_cookies(response)

	cookies = []
	for h in response.headers:
		cookies.append(h[1]) if h[0].startswith("Set-Cookie") else None

	#print "response cookies {}".format(cookies)

	def user_callback(error, result):
		if error:
			print "error for logoutuser {}".format(error)
		else:
			print "result for logoutuser {}".format(result)

	#frappe Admin must have the same address of reaction admin
	#db.users.update_one({"emails.address": {"$in": [email]}}, {"$set":{"profile.cookies": cookies}})
	db.users.update_one({"emails.address": {"$in": [email]}}, {"$set": {"profile.frappe_login": False}})
	#import meteor_ddp as ddp
	#try:
	#	ddp.logoutuser(email, None)
	#except Exception as e:
	#	print "logout user {} error: {}".format(email, e)


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


#insert user on mongodb. We need update password yet.
def mongodb_insert_user(doc, method):
	#if flag is True user already inserted in mongodb.
	if frappe.local.flags.is_from_efrappe:
		return

	#doc here is doc User class
	print "mongodb_insert_user doc is: {} o is {}".format(doc.email, method)



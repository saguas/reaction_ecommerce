import frappe
import inspect
import os



REACTION_WEB_HOST = None
REACTION_WEB_PORT = None
meteor_client = None
islogin = False



def get_admin_data():
	site_path = frappe.get_site_path()
	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	AdminEmail = site_config.get("admin_email")
	AdminPassword = site_config.get("admin_password")

	return (AdminEmail, AdminPassword)



def get_mongo_data():

	global REACTION_WEB_HOST
	global REACTION_WEB_PORT

	if REACTION_WEB_HOST and REACTION_WEB_PORT:
		return

	common_config = frappe.get_file_json("common_site_config.json")

	ddp = common_config.get("DDP_DEFAULT_CONNECTION_URL")
	ddp_url  = ddp.split("://")
	if(len(ddp_url) > 1):
		ddp_url = ddp_url[1].split(":")
	else:
		ddp_url = ddp_url[0].split(":")

	REACTION_WEB_HOST = ddp_url[0] or "localhost"
	REACTION_WEB_PORT = int(ddp_url[1].split("/")[0]) or 3000



get_mongo_data()

def callback_default_function(func_name):
	def callback_func(error, result):
		if error:
			print "from {} error: {}".format(func_name, result)
			return
		print "from {} result: {}".format(func_name, result)
	return callback_func



def reaction_connect_ddp(fn):
	"""
	decorator function
	"""
	def innerfn(*args, **kwargs):
		newargs = {}
		try:
			ddp_connect()
			fnargs, varargs, varkw, defaults = inspect.getargspec(fn)
			for a in fnargs:
				if a in kwargs:
					newargs[a] = kwargs.get(a)
			fn_result = fn(*args, **newargs)
			return fn_result

		except Exception as e:
			print "Problems in reaction_connect_ddp: {}\n".format(e)

	return innerfn

def reaction_login_ddp(callback=None):
	def reaction_ddp(fn):
		"""
		decorator function
		"""

		def innerfn(*args, **kwargs):
			newargs = {}
			try:
				admin, pwd = get_admin_data()
				meteor_login(admin, pwd, register_login_attempt(callback or callback_default_function("register_login_attempt")))
				fnargs, varargs, varkw, defaults = inspect.getargspec(fn)
				for a in fnargs:
					if a in kwargs:
						newargs[a] = kwargs.get(a)
				fn_result = fn(*args, **newargs)
				return fn_result

			except Exception as e:
				print "Problems in reaction_login_ddp: {}\n".format(e)

		return innerfn
	return reaction_ddp


def register_login_attempt(callback):
	def func(error=None, result=None):
		global islogin
		islogin = True
		callback and callback(error, result)
	return func


def meteor_login(username, pwd, callback, token=None):
	def login(client, user, password, token=None, callback=None):
		"""Login with a username and password

		Arguments:
		user - username or email address
		password - the password for the account

		Keyword Arguments:
		token - meteor resume token
		callback - callback function containing error as first argument and login data"""
		# TODO: keep the tokenExpires around so we know the next time
		#       we need to authenticate

		# password is already hashed
		hashed = password
		# handle username or email address
		if '@' in user:
			user_object = {
				'email': user
			}
		else:
			user_object = {
				'username': user
			}
		password_object = {
			'algorithm': 'sha-256',
			'digest': hashed
		}

		client._login_token = token
		client._login_data = {'user': user_object, 'password': password_object}

		if token:
			client._resume(token, callback=callback)
		else:
			client._login(client._login_data, callback=callback)

	global islogin
	if not islogin:
		client = ddp_connect()
		#client.login(username, pwd, token, callback)
		login(client, username, pwd, token, callback)


def ddp_connect():
	from MeteorClient import MeteorClient

	global meteor_client
	if not meteor_client:
		meteor_client = MeteorClient('ws://%s:%s/websocket' % (REACTION_WEB_HOST, REACTION_WEB_PORT))
		meteor_client.connect()
	return meteor_client


@reaction_login_ddp()
def create_meteor_user(email, pwd, username, callback):
	meteor_client.call('createFrappeUser', [email, pwd, username], callback)


@reaction_login_ddp()
def change_user_password(userId, newpwd, callback):
	meteor_client.call('changeFrappePassword', [userId, newpwd], callback)



def logout_callback(error=None, result=None):
	print "logout_callback error {} result {}".format(error, result)


@reaction_login_ddp(callback=logout_callback)
def logoutuser(email, callback):
	meteor_client.call('logoutFromFrappe', [email], callback)


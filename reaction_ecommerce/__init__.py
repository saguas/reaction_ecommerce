# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__version__ = '0.0.1'

import frappe

mongo_web_cli = None
mongo_desk_cli = None

MONGO_DEFAULT_PORT = 27017
MONGO_DEFAULT_HOST = "localhost"


def get_mongodesk_conf():
	default = frappe._dict({"host": MONGO_DEFAULT_HOST, "port": MONGO_DEFAULT_PORT})
	common_config = frappe.get_file_json("common_site_config.json")
	mongo = common_config.get("MONGODESK") or common_config.get("MONGO") or common_config.get("MONGOWEB")
	return mongo or default

def get_mongoweb_conf():
	default = frappe._dict({"host": MONGO_DEFAULT_HOST, "port": MONGO_DEFAULT_PORT})
	common_config = frappe.get_file_json("common_site_config.json")
	mongo = common_config.get("MONGOWEB") or common_config.get("MONGO")
	return mongo or default


def get_mongo_cli(type="web"):
	if type == "web":
		return get_mongo_web_cli()
	elif type == "desk":
		return get_mongo_desk_cli()
	else:
		return None

def get_mongo_web_cli():
	from pymongo import MongoClient

	global mongo_web_cli

	if (not mongo_web_cli):
		mconf = get_mongoweb_conf()
		mongo_web_cli = MongoClient(mconf.get("host"), int(mconf.get("port")))

	return mongo_web_cli


def get_mongo_desk_cli():
	from pymongo import MongoClient

	global mongo_desk_cli

	if (not mongo_desk_cli):
		mconf = get_mongodesk_conf()
		mongo_desk_cli = MongoClient(mconf.get("host"), mconf.get("port"))

	return mongo_desk_cli
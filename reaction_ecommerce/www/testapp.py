from __future__ import unicode_literals
import frappe, os
import urllib
from markupsafe import Markup
import hashlib
import json



meteor_config = {
			"meteorEnv":{"NODE_ENV":"development","TEST_METADATA":"{}"},
			"PUBLIC_SETTINGS":{},
		}

str_meteor_config = """{"meteorRelease":"%(release)s",
							"meteorEnv":{"NODE_ENV":"development","TEST_METADATA":"{}"},
							"PUBLIC_SETTINGS":{},
							"ROOT_URL":"%(root_url)s",
							"ROOT_URL_PATH_PREFIX":"%(url_prefix)s",
							"appId":"%(appid)s"}"""


def str_remove_newline_tabs(s):
	return s.encode('utf-8').replace("\n", "").replace("\t", "")

#not in use
def urlencode_filter(s):
	if type(s) == 'Markup':
		s = s.unescape()
	s = s.encode('utf8')
	s = urllib.quote_plus(s)
	return Markup(s)


def json_javascript_stringify(obj):
	return urllib.quote(unicode(json.dumps(obj)).encode('utf-8'), safe='~()*!.\'')

def set_meteor_config():
	common_config = frappe.get_file_json("common_site_config.json")
	site_path = frappe.get_site_path()

	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	meteor_config["DDP_DEFAULT_CONNECTION_URL"] = site_config.get("DDP_DEFAULT_CONNECTION_URL") or common_config.get("DDP_DEFAULT_CONNECTION_URL") or "http://localhost:3000/"
	meteor_config["ROOT_URL_PATH_PREFIX"] = site_config.get("ROOT_URL_PATH_PREFIX") or common_config.get("ROOT_URL_PATH_PREFIX") or ""
	root_url = site_config.get("ROOT_URL") or common_config.get("ROOT_URL") or "http://localhost:3000"
	if (not root_url.endswith("/")):
		root_url = root_url + "/"
	meteor_config["ROOT_URL"] = root_url


def get_meteor_ddp_default_conn_url():
	common_config = frappe.get_file_json("common_site_config.json")
	site_path = frappe.get_site_path()

	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	ddp = site_config.get("DDP_DEFAULT_CONNECTION_URL") or common_config.get("DDP_DEFAULT_CONNECTION_URL") or "http://localhost:3000/"

	return ddp

def get_reaction_webapp_path():
	common_config = frappe.get_file_json("common_site_config.json")

	site_path = frappe.get_site_path()

	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	meteor_app = site_config.get("reaction_webapp_path") or common_config.get("reaction_webapp_path") or ""

	return meteor_app

def get_meteor_root_url_paht_prefix():
	common_config = frappe.get_file_json("common_site_config.json")

	site_path = frappe.get_site_path()

	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	root_url_prefix = site_config.get("ROOT_URL_PATH_PREFIX") or common_config.get("ROOT_URL_PATH_PREFIX") or ""

	return root_url_prefix

def get_meteor_root_url():
	common_config = frappe.get_file_json("common_site_config.json")

	site_path = frappe.get_site_path()

	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	root_url = site_config.get("ROOT_URL") or common_config.get("ROOT_URL") or "http://localhost:3000"

	return root_url

def get_reaction_server_url():
	common_config = frappe.get_file_json("common_site_config.json")

	site_path = frappe.get_site_path()

	site_config = frappe.get_file_json(os.path.join(site_path, "site_config.json"))

	meteor_server = site_config.get("reaction_server") or common_config.get("reaction_server") or "http://localhost:3000"

	return meteor_server

def get_meteor_version(path):
	content = frappe.get_file_items(path)
	print "get_meteor_version {}".format(content)
	if content:
		return content[0]
	return ""

def get_meteor_id(path):
	content = frappe.get_file_items(path)
	print "get_meteor_id {}".format(content)
	if content:
		return content[0]
	return ""

def get_meteor_manifest(path):
	program_file = frappe.get_file_json(path)
	if(program_file):
		return program_file.get("manifest")

	return []


def calculateClientHash1(manifest, str_meteor_config):
	hash = hashlib.sha1()
	runtimeCfg = dict(meteor_config)

	runtimeCfg.pop("autoupdateVersion", None)
	runtimeCfg.pop("autoupdateVersionRefreshable", None)
	runtimeCfg.pop("autoupdateVersionCordova", None)
	runtimeCfg.pop("DDP_DEFAULT_CONNECTION_URL", None)

	#hash.update(str_meteor_config.encode('utf-8').replace("\n", "").replace("\t", ""))
	hash.update(str_remove_newline_tabs(str_meteor_config))
	for resource in manifest:
		if resource.get("where") == 'client' or resource.get("where") == 'internal':
			hash.update(resource.get("path"))
			hash.update(resource.get("hash"))
	return hash.hexdigest()

def calculateClientHashRefreshable(manifest, str_meteor_config):
	hash = hashlib.sha1()
	runtimeCfg = dict(meteor_config)

	runtimeCfg.pop("autoupdateVersion", None)
	runtimeCfg.pop("autoupdateVersionRefreshable", None)
	runtimeCfg.pop("autoupdateVersionCordova", None)
	runtimeCfg.pop("DDP_DEFAULT_CONNECTION_URL", None)

	#hash.update(str_meteor_config.encode('utf-8').replace("\n", "").replace("\t", ""))
	hash.update(str_remove_newline_tabs(str_meteor_config))
	for resource in manifest:
		if (resource.get("where") =='client' or resource.get("where") == 'internal') and resource.get("type") == "css":
			hash.update(resource.get("path"))
			hash.update(resource.get("hash"))
	return hash.hexdigest()

def calculateClientHash(manifest, str_meteor_config):
	hash = hashlib.sha1()
	runtimeCfg = dict(meteor_config)

	runtimeCfg.pop("autoupdateVersion", None)
	runtimeCfg.pop("autoupdateVersionRefreshable", None)
	runtimeCfg.pop("autoupdateVersionCordova", None)
	runtimeCfg.pop("DDP_DEFAULT_CONNECTION_URL", None)

	#hash.update(str_meteor_config.encode('utf-8').replace("\n", "").replace("\t", ""))
	hash.update(str_remove_newline_tabs(str_meteor_config))

	for resource in manifest:
		if (resource.get("where") == 'client' or resource.get("where") == 'internal') and resource.get("type") != "css":
			hash.update(resource.get("path"))
			hash.update(resource.get("hash"))
	return hash.hexdigest()


def _get_meteor_runtime_config():
	react_path = get_reaction_webapp_path()#"/Users/saguas/programacao/reaction_ecommerce_master_new/reaction"
	meteor_program_file_path = os.path.join(react_path, ".meteor/local/build/programs/web.browser/program.json")
	manifest = get_meteor_manifest(meteor_program_file_path)

	set_meteor_config()
	meteor_config["meteorRelease"] = get_meteor_version(os.path.join(react_path, ".meteor/release"))
	meteor_config["appId"] = get_meteor_id(os.path.join(react_path, ".meteor/.id"))
	sconfig = str_meteor_config % {"release":meteor_config["meteorRelease"], "root_url": meteor_config["ROOT_URL"], "url_prefix":meteor_config["ROOT_URL_PATH_PREFIX"], "appid":meteor_config["appId"]}
	meteor_config["autoupdateVersionRefreshable"] = calculateClientHashRefreshable(manifest, sconfig)
	meteor_config["autoupdateVersion"] = calculateClientHash(manifest, sconfig)
	meteor_config["autoupdateVersionCordova"] = "none"
	#meteor_config["ROOT_URL_PATH_PREFIX"] = "/react"

	return json_javascript_stringify(meteor_config)

def get_meteor_runtime_config():
	meteor_runtime_config = """__meteor_runtime_config__ = JSON.parse(decodeURIComponent("{meteor_runtime}"));""".format(meteor_runtime=_get_meteor_runtime_config())
	return meteor_runtime_config

def get_react_files():
	react_path = get_reaction_webapp_path()
	meteor_program_file_path = os.path.join(react_path, ".meteor/local/build/programs/web.browser/program.json")
	manifest = get_meteor_manifest(meteor_program_file_path)

	js_files = []
	css_files = []
	assets_files = []
	head_files = []

	for obj in manifest:
		path = obj.get("path")
		hash = obj.get("hash")
		url = obj.get("url")
		type = obj.get("type")
		if(type == "js"):
			#js_files.append(url)
			js_files.append(path)
		elif (type == "css"):
			#css_files.append(url)
			css_files.append(path)
		elif (type == "asset"):
			#assets_files.append(url)
			assets_files.append(path)
		elif (type == "head"):
			#head_files.append(path)
			head_files.append(path)
	return (js_files, css_files, assets_files, head_files)

def get_context(ctx):
	(ctx.js_files, ctx.css_files, ctx.assets_files, ctx.head_files) = get_react_files()
	ctx.meteor_runtime_config = get_meteor_runtime_config()
	#ctx.meteor_server = get_meteor_server_url()
	ctx.meteor_server = ""
	ctx.no_cache = True
	print "meteor_config {}".format(meteor_config)
	return ctx

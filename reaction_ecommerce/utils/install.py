import frappe
import os
from subprocess import check_call, Popen



def run_cmd(path, cmd, *args):
	proc = Popen([cmd] + list(args), cwd=path, close_fds=True)
	proc.wait()

def git(*args):
	return check_call(['git'] + list(args))



def install_desk():
	#site_path = frappe.get_site_path()
	module_path = frappe.get_module_path("reaction_ecommerce")
	reaction_home = os.path.abspath(os.path.join(module_path, ".."))
	reaction_www = os.path.abspath(os.path.join(reaction_home, "www"))
	reaction_desk = os.path.abspath(os.path.join(reaction_www, "deskreaction"))

	#make webreaction folder
	#frappe.create_folder(reaction_web)

	#git clone https://github.com/reactioncommerce/reaction.git
	#git("clone", "https://github.com/reactioncommerce/reaction.git")
	run_cmd(reaction_www, "git", "clone", "https://github.com/reactioncommerce/reaction.git", "deskreaction")

	#install meteor npm packages
	info = """
		*********************************************************
		*   installing desk meteor npm packages                 *
		*********************************************************
	"""
	print info
	run_cmd(reaction_desk, "meteor", "npm", "install")
	#git clone reaction efrappe
	#reaction_plugins_path = os.path.abspath(os.path.join(reaction_desk, "imports/plugins/custom"))
	#run_cmd(reaction_plugins_path, "git", "clone", "https://github.com/saguas/efrappe.git")

	#make public symlinks src .meteor/local/build/programs/web.browser and eweb in reaction_ecommerce/www/webreaction
	public_path = os.path.abspath(os.path.join(reaction_home, "public"))
	src = os.path.join(reaction_desk, ".meteor/local/build/programs/web.browser")
	dst = os.path.join(public_path, "desksrc")

	#make src .meteor/local/build/programs/web.browser
	os.symlink(src, dst)

	#make eweb reaction_ecommerce/www/webreaction
	src = reaction_desk
	dst = os.path.join(public_path, "edesk")
	os.symlink(src, dst)



def install_web():
	#site_path = frappe.get_site_path()
	module_path = frappe.get_module_path("reaction_ecommerce")
	reaction_home = os.path.abspath(os.path.join(module_path, ".."))
	reaction_www = os.path.abspath(os.path.join(reaction_home, "www"))
	reaction_web = os.path.abspath(os.path.join(reaction_www, "webreaction"))

	#make webreaction folder
	#frappe.create_folder(reaction_web)

	#git clone https://github.com/reactioncommerce/reaction.git
	#git("clone", "https://github.com/reactioncommerce/reaction.git")
	run_cmd(reaction_www, "git", "clone", "https://github.com/reactioncommerce/reaction.git", "webreaction")


	#git clone reaction efrappe
	reaction_plugins_path = os.path.abspath(os.path.join(reaction_web, "imports/plugins/custom"))
	run_cmd(reaction_plugins_path, "git", "clone", "https://github.com/saguas/efrappe.git")

	#install meteor npm packages
	info = """
		*********************************************************
		*   installing web meteor npm packages                  *
		*********************************************************
	"""
	print info
	run_cmd(reaction_web, "meteor", "npm", "install")
	#make public symlinks src .meteor/local/build/programs/web.browser and eweb in reaction_ecommerce/www/webreaction
	public_path = os.path.abspath(os.path.join(reaction_home, "public"))
	src = os.path.join(reaction_web, ".meteor/local/build/programs/web.browser")
	dst = os.path.join(public_path, "websrc")

	#make src .meteor/local/build/programs/web.browser
	os.symlink(src, dst)

	#make eweb reaction_ecommerce/www/webreaction
	src = reaction_web
	dst = os.path.join(public_path, "eweb")
	os.symlink(src, dst)


def after_install():
	install_web()
	#install_desk()

	#from reaction_ecommerce.commands.site import update_password
	#site = frappe.local.site
	#update_password([site], "")

	info = """
		**************************************************************
		*   Please run 												 *
		*		bench reaction_ecommerce set-admin-password          *
		*														 	 *
		*   Every time you need to change admin password you     	 *
		*   must run bench reaction_ecommerce set-admin-password 	 *
		*   to set a new password for administrator.             	 *
		*                                                        	 *
		*   Please run bench reaction_ecommerce for more help.   	 *
		**************************************************************
	"""
	print info


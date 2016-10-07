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

    run_cmd(reaction_www, "meteor", "npm", "install")
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
    install_desk()

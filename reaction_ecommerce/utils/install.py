import frappe
import os
from subprocess import check_call, Popen



def run_cmd(path, cmd, *args):
    proc = Popen([cmd] + list(args), cwd=path, close_fds=True)
    proc.wait()

def git(*args):
    return check_call(['git'] + list(args))


def after_install():
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

    #make public symlinks src .meteor/local/build/programs/web.browser and eweb in reaction_ecommerce/www/webreaction
    public_path = os.path.abspath(os.path.join(reaction_home, "public"))
    src = os.path.join(reaction_web, ".meteor/local/build/programs/web.browser")
    dst = os.path.join(public_path, "src")

    #make src .meteor/local/build/programs/web.browser
    os.symlink(src, dst)

    #make eweb reaction_ecommerce/www/webreaction
    src = reaction_web
    os.symlink(src, dst)

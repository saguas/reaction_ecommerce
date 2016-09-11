from __future__ import unicode_literals
import frappe

no_sitemap = 1
#frappe.local.no_cache = True
#frappe.conf.disable_website_cache = True


def get_home_page(args):
	print "get_home_page args {}".format(args)
	return "testapp.html"
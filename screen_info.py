#!/usr/bin/python
__author__    = "Fabian van der Hoeven"
__copyright__ = "Copyright (C) 2014 Vermont 24x7"
__version__   = "1.0"

import ConfigParser
import sys, os

sys.path.append('./lib')

from zabbix_api import ZabbixAPI, ZabbixAPIException
import json

class Config:
	def __init__(self, conf_file):
		self.config	     = None
		self.zabbix_frontend = ''
		self.zabbix_user     = ''
		self.zabbix_password = ''
		self.screen_name     = ''
		self.screen_hsize    = 0
		self.graph_width     = 0
		self.graph_height    = 0

		self.conf_file = conf_file
		if not os.path.exists(self.conf_file):
			print "Can't open config file %s" % self.conf_file
			exit(1)
		# Read common config
		self.config = ConfigParser.ConfigParser()
		self.config.read(self.conf_file)

	def parse(self):
		# Parse common config
		try:
			self.zabbix_frontend = self.config.get('common', 'zabbix_frontend')
		except:
			self.zabbix_frontend = 'localhost'
		try:
			self.zabbix_user = self.config.get('common', 'zabbix_user')
		except:
			self.zabbix_user = 'admin'
		try:
			self.zabbix_password = self.config.get('common', 'zabbix_password')
		except:
			self.zabbix_password = ''
		try:
			self.screen_name = self.config.get('screen', 'name')
		except:
			print "No name given for screen to create"
			sys.exit(1)
		try:
			self.screen_hsize = self.config.get('screen', 'hsize')
		except:
			self.screen_hsize = 2
		try:
			self.graph_width = self.config.get('screen', 'graph_width')
		except:
			self.graph_width = 500
		try:
			self.graph_height = self.config.get('screen', 'graph_height')
		except:
			self.graph_height = 100

def cleanup():
	pass

def main():
	import atexit
	atexit.register(cleanup)

	#get screens
	for screen in zapi.screen.get({ "output": "extend", "selectScreenItems": "extend" }):
		print json.dumps(screen, indent=4)
	sys.exit(1)

if  __name__ == "__main__":
	global config

	config_file = './screenbuilder.conf'

	config = Config(config_file)
	config.parse()
	zapi = ZabbixAPI(server=config.zabbix_frontend)

	try:
		print("Connecting to Zabbix API")
		zapi.login(config.zabbix_user, config.zabbix_password)
		print("Connected to Zabbix API Version: %s" % zapi.api_version())
	except ZabbixAPIException, e:
		print("Zabbix API connection failed")
		print("Additional info: %s" % e)
		sys.exit(1)
	main()

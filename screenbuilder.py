#!/usr/bin/python
__author__    = "Fabian van der Hoeven"
__copyright__ = "Copyright (C) 2014 Vermont 24x7"
__version__   = "1.0"

import ConfigParser
import sys, os
#import time, datetime
#import traceback
#from getpass import getpass
#import logging, logging.handlers, logging.config

sys.path.append('./lib')

from zabbix_api import ZabbixAPI, ZabbixAPIException
import json
import curses #curses is the interface for capturing key presses on the menu

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

def selectHostgroup():
	teller = 0
	hostgroups = {}
	for hostgroup in zapi.hostgroup.get({ "output": "extend", "filter": { "internal": "0"} }):
		teller+=1
		hostgroups[teller] = (hostgroup['name'], hostgroup['groupid'])
		print("selectHostgroup - Fetching hostgroups via API")
		print("selectHostgroup - Fetched hostgroups: %s" % hostgroups)
	hostgroupid = -1
	while hostgroupid == -1:
		os.system('clear')
		print "Hostgroups:"
		for hostgroup in hostgroups:
			print '\t%2d: %s (hostgroupid: %s)' % (hostgroup, hostgroups[hostgroup][0], hostgroups[hostgroup][1])
		try:
			hostgroupnr = int(raw_input('Select hostgroup: '))
			try:
				hostgroupid = hostgroups[hostgroupnr][1]
				hostgroupname = hostgroups[hostgroupnr][0]
			except KeyError:
				print("selectHostgroup - Raw input out of range, try again")
				print "\nCounting is not your geatest asset!"
				hostgroupid = -1
				print "\nPress a key to try again..."
				os.system('read -N 1 -s')
		except ValueError:
			print("selectHostgroup - Raw input not a number, try again")
			print "\nEeuhm... I don't think that's a number!"
			hostgroupid = -1
			print "\nPress a key to try again..."
			os.system('read -N 1 -s')
		except KeyboardInterrupt: # Catch CTRL-C
			pass
	print("selectHostgroup - Hostgroup selected (hostgroupid: %s, hostgroupname: %s)" % ( hostgroupid, hostgroupname))
	return (hostgroupid, hostgroupname)

def getHosts(hostgroupid):
	hosts = {}
	for host in zapi.host.get({ "output": "extend", "groupids" : [ hostgroupid ]}):
		hosts[host['name']] = (host['hostid'], getGraphs(host['hostid']))
	return hosts

def getGraphs(hostid):
	graphs = {}
	selected = '0'
	for graph in zapi.graph.get({ "output": "extend", "hostids":hostid }):
		graphs[graph['name']] = (graph['graphid'], selected)
	return graphs

def runmenu(menu, parent):

	h = curses.color_pair(1) #h is the coloring for a highlighted menu option
	n = curses.A_NORMAL #n is the coloring for a non highlighted menu option

	# work out what text to display as the last menu option
	if parent is None:
		lastoption = "Done selecting graphs!"
	else:
		lastoption = "Back to menu '%s'" % parent['title']

	optioncount = len(menu['options']) # how many options in this menu

	pos=0 #pos is the zero-based index of the hightlighted menu option.  Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what option has been selected
	oldpos=None # used to prevent the screen being redrawn every time
	x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program

	# Loop until return key is pressed
	while x !=ord('\n'):
		if pos != oldpos or x == 108 or x == 114 or x == 32:
			oldpos = pos
			screen.clear() #clears previous screen on key press and updates display based on pos
			screen.border(0)
			screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
			screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

			# Display all the menu items, showing the 'pos' item highlighted
			for index in range(optioncount):
				textstyle = n
				if pos==index:
					textstyle = h
				if 'graphid' in menu['options'][index]:
					if menu['options'][index]['selected'] == '0':
						check = '[ ]'
					elif menu['options'][index]['selected'] == 'l':
						check = '[l]'
					elif menu['options'][index]['selected'] == 'r':
						check = '[r]'
					elif menu['options'][index]['selected'] == '*':
						check = '[*]'
					screen.addstr(5+index,4, "%-50s %s" % (menu['options'][index]['title'], check), textstyle)
				else:
					screen.addstr(5+index,4, "%s" % menu['options'][index]['title'], textstyle)
			# Now display Exit/Return at bottom of menu
			textstyle = n
			if pos==optioncount:
				textstyle = h
			screen.addstr(5+optioncount,4, "%s" % lastoption, textstyle)
			screen.refresh()
			# finished updating screen

		try:
			x = screen.getch() # Gets user input
		except KeyboardInterrupt: # Catch CTRL-C
			x = 0
			pass

		# What is user input?
		if x == 258: # down arrow
			if pos < optioncount:
				pos += 1
			else:
				pos = 0
		elif x == 259: # up arrow
			if pos > 0:
				pos += -1
			else:
				pos = optioncount
		elif x == 108: # l(eft)
			if 'graphid' in menu['options'][pos]:
				if menu['options'][pos]['selected'] == 'l':
					menu['options'][pos]['selected'] = '0'
				else:
					menu['options'][pos]['selected'] = 'l'
			screen.refresh()
		elif x == 114: # r(ight)
			if 'graphid' in menu['options'][pos]:
				if menu['options'][pos]['selected'] == 'r':
					menu['options'][pos]['selected'] = '0'
				else:
					menu['options'][pos]['selected'] = 'r'
			screen.refresh()
		elif x == 32: # space, any
			if 'graphid' in menu['options'][pos]:
				if menu['options'][pos]['selected'] == '*':
					menu['options'][pos]['selected'] = '0'
				else:
					menu['options'][pos]['selected'] = '*'
			screen.refresh()
		elif x != ord('\n'):
			curses.flash()

	# return index of the selected item
	return pos

def processmenu(menu, parent=None):
	optioncount = len(menu['options'])
	exitmenu = False
	while not exitmenu: #Loop until the user exits the menu
		try:
			getin = runmenu(menu, parent)
		except Exception, e:
			curses.endwin()
			print "Something went wrong"
			print "Error: %s" % e
		if getin == optioncount:
			exitmenu = True
		elif menu['options'][getin]['type'] == 'MENU':
			processmenu(menu['options'][getin], menu) # display the submenu

def doMenu(menu_data):
	import curses #curses is the interface for capturing key presses on the menu, os launches the files
	global screen
	screen = curses.initscr() #initializes a new window for capturing key presses
	curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
	curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
	curses.start_color() # Lets you use colors when highlighting selected menu option
	screen.keypad(1) # Capture input from keypad

	# Change this to use different colors when highlighting
	curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background

	processmenu(menu_data)
	curses.endwin() #VITAL!  This closes out the menu system and returns you to the bash prompt.

def storeScreenGraphs(hostgroupid, hostgroupname, menu_data, screenid):
	row = 0
	num_hosts = len(menu_data['options'])
	for host in range(num_hosts):
		num_graphs = len(menu_data['options'][host]['options'])
		for graph in range(num_graphs):
			if menu_data['options'][host]['options'][graph]['selected'] == 'l':
				screenitem = {}
				screenitem['resourcetype'] = 0
				screenitem['resourceid'] = menu_data['options'][host]['options'][graph]['graphid']
				screenitem['screenid'] = screenid
				screenitem['width'] = config.graph_width
				screenitem['height'] = config.graph_height
				screenitem['x'] = 0 #left
				screenitem['y'] = row
				row += 1
				zapi.screenitem.create(screenitem)
	row = 0 #start at the top again
	for host in range(num_hosts):
                num_graphs = len(menu_data['options'][host]['options'])
                for graph in range(num_graphs):
                        if menu_data['options'][host]['options'][graph]['selected'] == 'r':
				screenitem = {}
				screenitem['resourcetype'] = 0
                                screenitem['resourceid'] = menu_data['options'][host]['options'][graph]['graphid']
                                screenitem['screenid'] = screenid
                                screenitem['width'] = config.graph_width
                                screenitem['height'] = config.graph_height
                                screenitem['x'] = 1 #right
                                screenitem['y'] = row
                                row += 1
				zapi.screenitem.create(screenitem)
	column = 0
	for host in range(num_hosts):
                num_graphs = len(menu_data['options'][host]['options'])
                for graph in range(num_graphs):
                        if menu_data['options'][host]['options'][graph]['selected'] == '*':
				screenitem = {}
				screenitem['resourcetype'] = 0
                                screenitem['resourceid'] = menu_data['options'][host]['options'][graph]['graphid']
                                screenitem['screenid'] = screenid
                                screenitem['width'] = config.graph_width
                                screenitem['height'] = config.graph_height
                                screenitem['x'] = column
                                screenitem['y'] = row
				if column == 0:
					column = 1
				else:
					column = 0
					row += 1
				zapi.screenitem.create(screenitem)

def checkScreenGraphs(hostgroupid, hostgroupname, menu_data):
	num_hosts = len(menu_data['options'])
	num_selected = 0
	print "Hostgroup '%s':" % hostgroupname
	for host in range(num_hosts):
		print '\t%s' % menu_data['options'][host]['title']
		num_graphs = len(menu_data['options'][host]['options'])
		selected_graphs_host = 0
		for graph in range(num_graphs):
			if menu_data['options'][host]['options'][graph]['selected'] != '0':
				selected_graphs_host += 1
		if selected_graphs_host > 0:
			for graph in range(num_graphs):
				if menu_data['options'][host]['options'][graph]['selected'] == 'l':
					num_selected += 1
					graph_type = "Left"
				elif menu_data['options'][host]['options'][graph]['selected'] == 'r':
					num_selected += 1
					graph_type = "Right"
				elif menu_data['options'][host]['options'][graph]['selected'] == '*':
					num_selected += 1
					graph_type = "Anywhere"
				if menu_data['options'][host]['options'][graph]['selected'] != '0':
					print "\t\t%-18s: %s" % (graph_type, menu_data['options'][host]['options'][graph]['title'])
		else:
			print "\t\tNo graphs selected for this host"
	if num_selected > 0:
		antwoord = ""
		while antwoord not in ["yes", "Yes", "no", "No"]:
			try:
				antwoord = str(raw_input('\nDo you want to create a screen called "%s" with these graphs? (Yes/No): ' % config.screen_name))
			except KeyboardInterrupt: # Catch CTRL-C
				pass
		if antwoord in ["yes", "Yes"]:
			print "OK"
			from math import fmod
			vsize = num_selected / 2 + fmod(num_selected, 2)
			zapi.screen.create({"name": config.screen_name, "hsize": config.screen_hsize, "vsize": vsize})
			screenid = zapi.screen.get({ "output": "extend", "filter": { "name": config.screen_name} })[0]['screenid']
			storeScreenGraphs(hostgroupid, hostgroupname, menu_data, screenid)
		else:
			print "Then not"
	else:
		print "\nNothing selected. Nothing to do. Just wasting time."

def cleanup():
	pass

def main():
	import atexit
	atexit.register(cleanup)

	result = zapi.screen.exists({ "name": config.screen_name})
	while result:
		# Screen allready exists
		print "\nScreen %s allready exists.\nSelect a different name." % config.screen_name
		screen_name = ""
		while screen_name == "":
                        try:
                                screen_name = str(raw_input('\nNew screen name: '))
                        except KeyboardInterrupt: # Catch CTRL-C
                                pass
		config.screen_name = screen_name
		result = zapi.screen.exists({ "name": config.screen_name})
	hostgroupid, hostgroupname = selectHostgroup()
	hosts = getHosts(hostgroupid)

	# Build the menus
	menu = {'title': 'Host list', 'type': 'MENU', 'subtitle': 'Select a host...'}
	menu_options = []
	for host in sorted(hosts.iterkeys()):
		menu_hosts = {}
		menu_hosts['title'] = host
		menu_hosts['hostid'] = hosts[host][0]
		menu_hosts['type'] = 'MENU'
		menu_hosts['subtitle'] = 'Select the graphs for the screen. Use "l" to place graph in left column, "r" for the right column, space if it doesn\'t matter'
		graphs = hosts[host][1]
		host_options = []
		for graph in sorted(graphs.iterkeys()):
			menu_graphs = {}
			menu_graphs['title'] = str(graph)
			menu_graphs['type'] = 'GRAPHID'
			menu_graphs['graphid'] = graphs[graph][0]
			menu_graphs['selected'] = graphs[graph][1]
			host_options.append(menu_graphs)
		menu_hosts['options'] = host_options
		menu_options.append(menu_hosts)
	menu['options'] = menu_options

	doMenu(menu)
	os.system('clear')
	checkScreenGraphs(hostgroupid, hostgroupname, menu)

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

#!/usr/bin/python

import re
import json
import requests
import collectd

CONFIGS = { }
SPLUNK_DATA = {}
VERBOSE_LOGGING = False

# This function is called firest and, it parsers the module config block
# Gathering all the useful information
# This function needs to be registed or else it is of no use :)

def configure_callback(conf):
	"""Receive configuration block"""
	collectd.debug("in configure")

	host         = None
	port         = None
	url          = None
	username     = None
	userpassword = None
	instance     = None

	for node in conf.children:
		key = node.key.lower()
		val = node.values[0]

		log_verbose('Analyzing config %s key (value: %s)' % (key, val))

		if key == 'host':
			host = val
		elif key == 'port':
			port = int(val)
		elif key == 'url':
			url = val
		elif key == 'username':
			username = val
		elif key == 'userpassword':
			userpassword = val
		elif key == 'instance':
			instance = val
		elif key == 'verbose':
			global VERBOSE_LOGGING
			VERBOSE_LOGGING = str2bool(node.values[0]) or VERBOSE_LOGGING

		# Path is child node 
		elif key == 'path':
			# this loops fetches the data with in child node
			for childNode in node.children:
				childKey = childNode.key.lower()
				childVal = childNode.values[0]
				# we have a key called type in child node , which specifies the data 'type' as found in types.db
				if childKey == 'type':
					global SPLUNK_INFO
					SPLUNK_DATA[val] = childVal

		else:
			collectd.warning('splunkData plugin: unknown config key %s' % key )


	log_verbose('Registed splunkData with: host=%s, port=%s, url=%s, userName=%s, userPassword=%s, Intance=%s' % ( host, port, url, username, userpassword, instance))

	CONFIGS.update({ 'host': host, 'port': port, 'url': url, 'username': username, 'userpassword': userpassword, 'instance': instance })

# Pthon does not have any built in funtion 
# which can conver the string value "true" or "false" to bollen True or False , hence this!
def str2bool(value):
	return value.lower in ("yes","true","1","t","y")

# This function is called next! ( i.e. 2nd) and last registered function
def read_callback():
	log_verbose('Config Hash  %s' % CONFIGS)
	get_metrics(CONFIGS)

def get_metrics( conf ):

	data = fetch_data(conf)

	if not data:
		collectd.error('splunkData plugin: No data received')
		return 

	if conf['instance']: 
		plugin_instance = conf['instance']
	else:
		plugin_instance = '{host}:{port}'.format(host=conf['host'],port=conf['port'])

	for composite_key,val in SPLUNK_DATA.iteritems():
		dispatch_data(data,composite_key,val,plugin_instance)

		
def fetch_data(conf):
	"""Connect to Splunk to get the Data"""
	log_verbose('In fetch_data')
	log_verbose('===============')
	try:
		requestURL =  'https://' + conf['host'] + ':' + str(conf['port']) + '/' + conf['url']
		log_verbose('Connecting to url %s with userName=%s and, userPassword=%s' %(requestURL,conf['username'],conf['userpassword']))
		webRequest  = requests.get(requestURL, auth=(conf['username'],conf['userpassword']))
		content = json.loads(webRequest.text)
		data =json.loads(content['entry'][0]['content']['data'])
		log_verbose('data: %s' % data)

	except requests.exceptions:
		collectd.error('Exception: %s' % e)
		return None
		
	log_verbose('Received data: %s' % data )

	return data

#This function dispatches the value of key
def dispatch_data(data,composite_key,type,plugin_instance=None,type_instance=None):
	""" Dispatch the Data"""
	log_verbose('In Dispatch')
	log_verbose('===========')
	
	if plugin_instance is None:
		plugin_instance = 'unkown_splunkData'
		collectd.error('splunkData plugin: Data key not found: %s' %kcomposite_key)

	if type_instance is None:
		type_instance = composite_key

	#split the composite key into it's components	
	keys = composite_key.split('/')

	# assigning value of first data item to value
        # this should speed up recursive lookup done below in for loop
        key = keys.pop(0)
	value = data[key]

	# recurse until final value is found!
	for key in keys:
		value = value[key]

	log_verbose('Sending Value: %s=%s' % (type_instance, value))

	val = collectd.Values(plugin='splunkData')
	val.type = type
	val.type_instance = type_instance
	val.plugin_instance = plugin_instance
	val.values = [value]
	val.dispatch()

# print/display verbose information
def log_verbose(msg):
	"""Print the Verbose message if asked for it"""
	if not VERBOSE_LOGGING:
		return 
	collectd.info('SplunkData Plugin [verbose]: %s' %  msg)
	
# call back function registraton
collectd.register_config(configure_callback)
collectd.register_read(read_callback)

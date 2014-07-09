#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import time

class result(object):
	def __init__(self, uid, success, message, history=None):
		self.uid = uid
		self.read()
		# Overwrite populated values
		self.success = success
		self.message = message
		self.icon = self._marker()
		self.time = time.ctime()

		if not hasattr(self, 'history'):
			self.history = []

		if history:
			self.history.insert(0, history)
			self.history = self.history[:20]
		
	def _marker(self):
		markers = {
			True: '&#10004;',
			False: '&#10008;',
		}

		return markers.get(self.success)

	def read(self):
		mydir = os.path.dirname(__file__)
		myfile = os.path.join(mydir, 'data', self.uid + 'dat.json')
		if os.path.exists(myfile) and os.path.isfile(myfile):
			with open(myfile, 'r') as ouf:
				jsdata = json.load(ouf)
				for k, v in jsdata.items():
					setattr(self, k, v)


	def write(self):
		mydir = os.path.dirname(__file__)
		with open(os.path.join(mydir, 'data', self.uid + 'dat.json'), 'w+') as ouf:
			json.dump(self.__dict__, ouf)

	def __repr__(self):
		return '''%s\t-\t%s''' % (self._marker(), self.message)


class check(object):
	def __init__(self, func='', **kwargs):
		self.func = getattr(checks, func)
		self.uid = hashlib.sha1(func + ''.join(kwargs.values())).hexdigest()
		self.kwargs = kwargs

	def run(self):
		try:
			r = result(self.uid, **self.func(**self.kwargs))
			r.write()
		except Exception, e:
			r = result(self.uid, success=False, message='Fallthrough: ' + repr(e))
			r.write()


class checks(object):
	'''Container for checks, allows us to use getattr(<string>) easily'''

	@staticmethod
	def check_nfs(host, port=111):
		import binascii
		import socket
		result = {}

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		s.connect((host, port))
		# message('check', 'Socket connected to %s:%d' % (host, port))
		rawmsg = '8000003c9f0900650000000000000002000186a00000000200000000000000010000001400000000000000000000000000000000000000000000000000000000'
		msg = binascii.a2b_hex(rawmsg)
		if s.send(msg) != len(msg):
			return dict(success=False, message='Failed to send NFS request to %s' % host)

		data = s.recv(10)

		if data:
			result['success'] = True
			result['message'] = 'Data recieved from NFS request to %s' % host
		s.shutdown(1)
		s.close()

		return result

	@staticmethod
	def check_http(host):
		import socket
		import httplib

		try:
			conn = httplib.HTTPConnection(host)
			conn.request("GET","/")
			res = conn.getresponse()
			data = res.read()

			if data and res.status == 200:
				return dict(success=True, message='HTTP request to %s: OK' % host, history=len(data))
			return dict(success=False, message='HTTP error for %s: %s' % (host, res.reason))
		except socket.gaierror:
			return dict(success=False, message='HTTP request failed to resolve %s' % host)

	@staticmethod
	def check_https(host):
		import socket
		import httplib

		try:
			conn = httplib.HTTPSConnection(host)
			conn.request("GET","/")
			res = conn.getresponse()
			data = res.read()

			if data and res.status == 200:
				return dict(success=True, message='HTTPS request to %s: OK' % host, history=len(data))
			return dict(success=False, message='HTTPS error for %s: %s' % (host, res.reason))
		except socket.gaierror:
			return dict(success=False, message='HTTPS request failed to resolve %s' % host)


def group(lst, n):
	for i in range(0, len(lst), n):
		val = lst[i:i+n]
		if len(val) == n:
			yield tuple(val)


if __name__ == '__main__':
	'''Called by: python objstat.py func check_http host reddit.com'''

	import sys
	check(**dict(group(sys.argv[1:], 2))).run()

	# Index our data
	with open(os.path.join('data', 'index.json'), 'w+') as ouf:
		json.dump(os.listdir('data'), ouf)

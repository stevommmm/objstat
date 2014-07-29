#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import time

import sys
import inspect

from checks import *

def filter_functions():
	funcs = []
	def _inspect(f):
		return inspect.getmembers(f, inspect.isfunction)

	def _filter(f):
		return not f[0].startswith('__')

	for f in [x[1] for x in sys.modules.items() if 'checks' in x[0]]:
		funcs += _inspect(f)

	return dict(filter(_filter, funcs))

available_checks = filter_functions()

class result(object):
	def __init__(self, uid, success, message, history=True):
		self.uid = uid
		self.read()

		if not hasattr(self, 'history'):
			self.history = []
		else:
			if history:
				self.history.insert(0, self.message + '<span>' + self.time + '</span>')
				self.history = self.history[:20]

		# Overwrite populated values
		self.success = success
		self.message = message
		self.icon = self._marker()
		self.time = time.ctime()

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
		if not func in available_checks:
			print('Function not found')
			sys.exit(1)
		self.func = available_checks.get(func)
		self.uid = hashlib.sha1(func + ''.join(kwargs.values())).hexdigest()
		self.kwargs = kwargs

	def run(self):
		try:
			r = result(self.uid, **self.func(**self.kwargs))
			r.write()
		except Exception, e:
			r = result(self.uid, success=False, message='Fallthrough: ' + repr(e))
			r.write()


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
	mydir = os.path.dirname(__file__)
	with open(os.path.join(mydir, 'data', 'index.json'), 'w+') as ouf:
		i = []
		for f in os.listdir(os.path.join(mydir, 'data')):
			i.append(os.path.split(f)[-1])
		json.dump(i, ouf)

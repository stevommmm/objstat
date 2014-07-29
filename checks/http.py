def check_http(host):
	import socket
	import httplib

	try:
		conn = httplib.HTTPConnection(host)
		conn.request("GET","/")
		res = conn.getresponse()
		data = res.read()

		if data and res.status == 200:
			return dict(success=True, message='HTTP request to %s: OK' % host)
		return dict(success=False, message='HTTP error for %s: %s' % (host, res.reason))
	except socket.gaierror:
		return dict(success=False, message='HTTP request failed to resolve %s' % host)


def check_https(host):
	import socket
	import httplib

	try:
		conn = httplib.HTTPSConnection(host)
		conn.request("GET","/")
		res = conn.getresponse()
		data = res.read()

		if data and res.status == 200:
			return dict(success=True, message='HTTPS request to %s: OK' % host)
		return dict(success=False, message='HTTPS error for %s: %s' % (host, res.reason))
	except socket.gaierror:
		return dict(success=False, message='HTTPS request failed to resolve %s' % host)
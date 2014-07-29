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

def check_irc(host, port=6667):
	import socket
	import time
	import random

	nick = 'objstat_' + ''.join(map(chr, [random.randrange(97, 122) for x in list(range(5))]))

	result = dict(success=False, message='Failed to connect to %s' % host)

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.connect((host, port))

		s.send('NICK %s\r\n' % nick)
		s.send('USER %s * * :Monitoring bot\r\n' % nick)

		time.sleep(5)

		data = s.recv(300)

		if 'NOTICE' in data:
			result['success'] = True
			result['message'] = 'IRC services running at %s' % host
		else:
			result['message'] = 'Failed to complete irc handshake with %s' % host

		time.sleep(10)

		s.send('QUIT :Done monitoring')
		s.shutdown(1)
		s.close()
	except socket.gaierror:
		return dict(success=False, message='Failed to resolve irc server: %s' % host)
	finally:
		return result
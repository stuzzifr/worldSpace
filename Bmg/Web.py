import urllib
import re

address = 'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/seine_saint_denis/?th=1&ps=1&pe=4&ret=2'

sock = urllib.urlopen(address)
html = sock.read()
sock.close()

reg = re.search(r'(studio)(.+)', html)

print html

if reg:
	print reg.groups()
else:
	print 'found nothing'

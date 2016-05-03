# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.http import HttpResponse, HttpResponseNotFound
from django.core.mail import send_mail
import urllib2
import re
import json
import datetime
from bs4 import BeautifulSoup

patt = re.compile('[ \n]')
site = 'http://www.leidsa.com/sorteos-anteriores'
main_site = 'http://www.leidsa.com/'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def games(request):
	# Http request to web server
	req = urllib2.Request(site, headers=hdr)
	main_req = urllib2.Request(main_site, headers=hdr)

	try:
	    page = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
	    return HttpResponse(e.fp.read())

	try:
	    main_page = urllib2.urlopen(main_req)
	except urllib2.HTTPError, e:
	    return HttpResponse(e.fp.read())

	# Gets the pages content
	content = page.read()
	main_content = main_page.read()

	d = []
	# Gets the table data from the html content
	try:
		table = re.search(r'<tbody>([.\n\s\S]+)<\/tbody>', content, re.MULTILINE)
	except:
		return HttpResponseNotFound("No data")
	
	slider = BeautifulSoup(main_content, "html.parser")

	monto = int(slider.find(id="title-monto").string)
	loto = int(slider.find(id="acumu-loto").string)
	loto_mas = int(slider.find(id="acumu-mas").contents[1].replace('\u00a0', ''))

	next_game = {"amount": monto, "loto": loto, "loto_mas": loto_mas}

	# Counter initialization
	c = 0;

	if table is not None:
		try:
			g = table.group(1)
			# Gets the rows content in the table
			
			rows = re.findall(r'<tr>([.\n\s\S]+?)<\/tr>', g, re.MULTILINE)
			# Iterates over every row
			for r in rows:
				# Increments the counter
				c += 1
				# If the counter is greater than 150 it breaks
				if c > 150:
					break
				# Creates an object with the data in the rows
				cells = re.findall(r'<td>([.\n\s\S]+?)<\/td>', r, re.MULTILINE)
				date = cells[0]
				game = cells[2]
				shift = cells[3].replace('&nbsp;', '')
				numbers = map(lambda x: int(x), patt.split(cells[4]))
				d.append({'date': date, 'game': game, 'shift': shift, 'numbers': numbers})

			gmt4 = GMT4()
			jsonFile = {"datestamp": datetime.datetime.now(gmt4).strftime("%d/%m/%y %H:%M %p"),
                "saved_amount": next_game,
                "games": d}
			return HttpResponse(json.dumps(jsonFile, sort_keys=True, indent=4, separators=(',', ': ')))
		except:
			HttpResponseNotFound("No data")
	else:
		return HttpResponseNotFound("No data")

class GMT4(datetime.tzinfo):
	def utcoffset(self,dt):
		return datetime.timedelta(hours=-4)
	def tzname(self,dt):
	       return "GMT -4"
	def dst(self,dt):
		return datetime.timedelta(0)


def feedback(request):
	"""" Used to receive email from feedback """
	if request.method == 'POST':
		subject = request.POST.get("subject", "")
		message = request.POST.get("message", "")
		#from_email = request.POST.get("mail", "")
		from_email = "bancas@rutas.duoevents.net"
		recipient_list = ["bancas@rutas.duoevents.net"]
		send_mail(subject, 
			message, 
			from_email, 
			recipient_list, 
			fail_silently=False, 
			auth_user="bancas@rutas.duoevents.net", 
			auth_password= "bancas1314")
		return HttpResponse("Envio satisfactorio")
	return HttpResponse("Envio erroneo")
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fix Python 2.x.
try:
	input = raw_input
except NameError:
	pass

from apiclient.discovery import build
from babel import Locale
import pprint
import getopt
import argparse
import json




def translate(fallback, text, out, flag):
	testo=text

	testo=testo

	service = build(
		'translate',
		'v2',
		developerKey='{YOUR-GOOGLE-DEVELOPER-KEY}'
	)

	fro=fallback
	to=out

	phrase = "***"

	try:
		jsonres = service.translations().list(source=fro, target=out, q=[testo]).execute()
		phrase = jsonres['translations'][0]['translatedText']
	
	except:
		print("Errore")
	
	if flag == False:
		return phrase
	else:
		flag == True
		translate(fallback, phrase, "en", flag)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fix Python 2.x.
try:
	input = raw_input
except NameError:
	pass

from babel import Locale
from shutil import copyfile
from xml.dom import minidom
from service import translate

import xml.etree.ElementTree as ET
import sys
import os
import io


def checkTranslation(translation):
	if translation == "***":
		print("Errore: Lingua di output non trovata")
		sys.exit()

def main():

	# Paths
	scriptDirPath = os.path.dirname(os.path.realpath(__file__))
	scriptBasename = os.path.basename(os.path.realpath(__file__))
	originFilePath = ''
	xmlPath = scriptDirPath+'/copyOrigin.xml'
	fallbackPath = 'languages/fallback'
	languagesPath = 'languages'
	languagePath = 'languages/language'
	sectionsPath = 'sections'
	messagesPath = 'messages'
	sectionTranslationPath = 'label/translation'
	messageTranslationPath = 'translation'
	savePath = ""
	finalRes = ""

	if not len(sys.argv) == 2:
		print('usage: python ' + scriptBasename + ' [xmlFilePath]')
		sys.exit()
	originFilePath = os.path.realpath(str(sys.argv[1]))

	# Security copy
	copyTree = ET.parse(originFilePath)
	copyTree.write(xmlPath, encoding='utf-8', xml_declaration=True)

	# Main values
	tree = ET.parse(xmlPath)
	root = tree.getroot()

	# Global values

	out = ""
	while(True):
		out = input('Lingua di output: ')
		if len(out) == 0:
			print('Errore: il valore non può essere nullo.')
		else:
			break
	fallback = root.find(fallbackPath).text
	flagOverride = False
	languagesObj = root.find(languagesPath)
	languagesFindAll = root.findall(languagePath)
	languageLabel = ''
	fallbackObj = root.find(fallbackPath)
	sectionsObj = root.find(sectionsPath)
	messagesObj = root.find(messagesPath)
	falgLanguageTranslated = False


	# Functions
	def getSectionsList():
		funSectionsList = []
		for itmFunSections in sectionsObj:
			funSectionsList.append(itmFunSections)
		return funSectionsList

	def getMessagesList():
		funMessagesList = []
		for itmFunMessages in messagesObj:
			funMessagesList.append(itmFunMessages)
		return funMessagesList


	if out == fallback:			# Check input language != fallback language
		print('Lingua già presente.')
		sys.exit()


	# Check language already translated
	if not languagesObj.find('language[@code="' + out + '"]') is None:
		falgLanguageTranslated = True
		while(True):
			modeSelection = input('Lingua già tradotta. Completare la traduzione, sovrascriverla o uscire? (c/s/u) ')
			if modeSelection == 'c':
				flagOverride = False
				break
			elif modeSelection == 's':
				flagOverride = True
				break
			elif modeSelection == 'u':
				sys.exit()


	try:  		# From short to long language name
		locale = Locale(out)
		languageLabel = locale.display_name
		leng = locale.get_display_name('it')
		leng = locale.display_name + ' (' + locale.get_display_name('it') + ')'
		while(True):
			goonRes = input('Lingua selezionata: ' + leng +
						 '. Continuare? (y/n) ')
			if goonRes == 'n':
				sys.exit()
			if goonRes == 'y' or goonRes == 'n':
				break
	except SystemExit:
		sys.exit()
	except:
		if falgLanguageTranslated:
			languageLabel = languagesObj.find('language[@code="'+out+'"]').text
		else:
			while(True):
				languageLabel = input('Lingua non riconosciuta, scrivi il nome a mano: ')
				if len(languageLabel) == 0:
					print('Errore: il valore non può essere vuoto')
				else:
					break
	languagesObj.remove(fallbackObj)  		# Remove existing fallback element
	elem = ET.Element('fallback') 			# Insert fallback on top
	elem.text = fallback
	languagesObj.insert(0, elem)


	if languagesObj.find('language[@code="'+out+'"]') is None:
		ET.SubElement(languagesObj, 'language', code=out)		# Add language
		languagesObj.find('language[@code="'+out+'"]').text = languageLabel


	# Sections translation
	for child in getSectionsList():
		sectionPhrase = child.find('label/translation[@code="'+fallback+'"]').text
		translation = translate(fallback, sectionPhrase, out, False) 	# Translate
		checkTranslation(translation)
		if flagOverride:
			if child.find('label/translation[@code="'+out+'"]') is None:
				ET.SubElement(child.find('label'), 'translation', code=out)
			child.find('label/translation[@code="'+out+'"]').text = translation
		else:
			if child.find('label/translation[@code="'+out+'"]') == None:
				ET.SubElement(child.find('label'), 'translation', code=out)
				child.find('label/translation[@code="'+out+'"]').text = translation


	# Messages translation
	for child in getMessagesList():
		messagePhrase = child.find('translation[@code="'+fallback+'"]').text
		translation = translate(fallback, messagePhrase, out, False) 	# Translate
		checkTranslation(translation)
		if flagOverride:
			if child.find('translation[@code="'+out+'"]') is None:
				ET.SubElement(child, 'translation', code=out)
			child.find('translation[@code="'+out+'"]').text = translation
		else:
			if child.find('translation[@code="'+out+'"]') is None:
				ET.SubElement(child, 'translation', code=out)
				child.find('translation[@code="'+out+'"]').text = translation


	tree.write(xmlPath, encoding="utf-8", xml_declaration=True)  	# Reload xml file


	# Edit, indent and save
	import xml.dom.minidom # DO NOT MOVE. Conflict may happen

	xml = xml.dom.minidom.parse(xmlPath)
	pretty_xml_as_string = xml.toprettyxml() # Indent
	arr = pretty_xml_as_string.split('\n')
	for f in arr:
		if '<' in f and '>' in f:
			finalRes+=f+'\n'

	while(True):
			saveRes = input('Sovrascrivere il file "' + originFilePath + '"? (y/n) ')
			if saveRes == 'n':
				savePath = ""
				while(True):
					savePath = input('Scrivere il percorso: ')
					if len(savePath) == 0:
						print('Errore: valore nullo.')
					else:
						break
			elif saveRes == 'y':
				savePath = originFilePath
			if saveRes == 'y' or saveRes == 'n':
				break
	try:
		with io.open(savePath, 'w', encoding='utf-8') as f:
			f.write(finalRes)
			print ('File salvato correttamente.')
	except:
		print ('Errore durante il salvataggio.')
	os.remove(xmlPath)


main()

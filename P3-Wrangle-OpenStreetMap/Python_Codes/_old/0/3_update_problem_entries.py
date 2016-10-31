#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Script #3
0. Preparatory work.
- Check that the prolem entries now contain the correct information and are stored in 'Corrected_Entries/' folder.
- Check that documents/elements to be dropped from the XML dataset are correctly marked in the INDEX file.

1. Run this script only once.
      $ python 3_update_problem_entries.py

2. Move on to the next script.

"""

# PACKAGES
import xml.etree.cElementTree as ET
from os import remove
from shutil import move

from helperFunctions import getList

# FILE PATH
path = "../Dataset/"
filename = "singapore.xml"

XMLFILE_IN = path + filename

# PREP WORK
list_Update = getList("Corrected_Entries/INDEX")

k = 1 # Parameter: take every k-th top level element

# FUNCTIONS
def update_Element(element):
    name = element.tag + element.attrib['id'] 
    noUpdate = "***" + name
    if noUpdate in list_Update:
        return None
    elif name in list_Update:
        file = "Corrected_Entries/" + name
        with open(file, 'r') as f:
            data = f.readlines()
        return ET.fromstringlist(data)
    else:
        return element

def get_element(file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag
    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(file, events = ('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:            
            yield elem
            root.clear()

# MAIN SCRIPT
with open("_temp/temp.xml", 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n ')
    #  Write every kth top level element
    for i, element in enumerate(get_element(XMLFILE_IN)):
        if i % k == 0:
            element = update_Element(element)
            if element is not None:
                output.write(ET.tostring(element, encoding='utf-8'))
    output.write('</osm>')

move("_temp/temp.xml", XMLFILE_IN)

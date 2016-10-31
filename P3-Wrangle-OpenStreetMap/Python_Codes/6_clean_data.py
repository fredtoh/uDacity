"""
# Scripts #5 and #6

1. Run Script #5 for the dry-run. (XML file will not be altered.)
      $ python 5_format_and_map_dryrun.py > Logs/DryRun_FnM.log

2. Review the DryRun_FnM.log to compare the changes between the original and the modified street name.
   - Any problem with the formatting and mapping of text should be detected at this stage.
   - If the formatting and mapping is faulty, Script #5 should be reviewed and modified.
   - Repeat Steps 1 and 2 until satisfactory.

3. Run Script #6 for the actual run. (XML file will be altered.)
      $ python 6_clean_data.py > Logs/Cleaned.log

4. Review the Cleaned.log. The output should be identical to DryRun_FnM.log.


"""

# PACKAGES
from helperFunctions import getDict
import string
import re
import xml.etree.cElementTree as ET

# FILE PATH
path = "../Dataset/"
filename = "singapore.xml"

XMLFILE = path + filename

# PREP WORK
MAPPING = getDict("Lists/MAPPING")

# REGEX MATCHING (Use re.search and re-assemble the groups, after formatting)
cap1 = re.compile("(^|.*\s)([dolDOL]')(.*)") # Special caps after apostrophe, e.g. D'Almeida
cap2 = re.compile("(^|.*\s)([mM]a?c)(.*)") # Mc + Mac words
cap3 = re.compile("(.*[a-z]-)([a-zA-Z].*)") # Special caps after dash, e.g. One-North
st1 = re.compile("(^|.*\s)([sS]t.?|[sS]aint)(\s[A-Za-z].*)") # Saint streets

sp1 = re.compile("(.*\s)([0-9]+)([A-Za-z]+)(\s.*)") # Special case for street branches where an alphabet follows a numeral.



# FUNCTIONS
def is_street_name(elem):
    try:
        return (elem.attrib['k'] == "addr:street")
    except:
        return False

def is_SaintStreet(street_name):
    return st1.match(street_name) is not None

def format_SpecialCap(street_name):
    g = cap1.search(street_name)
    if g is not None:
        return g.group(1) + string.capwords(g.group(2)) + string.capwords(g.group(3))
    else:
        return street_name

def format_McMac(street_name):
    g = cap2.search(street_name)
    if g is not None:
        return g.group(1) + string.capwords(g.group(2)) + string.capwords(g.group(3))
    else:
        return street_name

def format_DashCap(street_name):
    g = cap3.search(street_name)
    if g is not None:
        return g.group(1) + string.capwords(g.group(2))
    else:
        return street_name

def format_Special(street_name):
    g = sp1.search(street_name)
    if g is not None:
        return g.group(1) + g.group(2) + g.group(3).upper() + g.group(4)
    else:
        return street_name

def mapName(street_name, map = MAPPING):
    mapped_Name = street_name
    for word in street_name.split():
        if word in map.keys():
            mapped_Name = re.sub(word, map[word], mapped_Name)
    return mapped_Name

def check_Diff(name1, name2, element):
    if name1 != name2:
        print "(Type: %s, ID: %s) %s ==> %s" % (element.tag, element.get('id'), name1, name2)

def format_and_map(element):
    # YOUR CODE HERE
    for item in element:
        if is_street_name(item):
            st_name = string.capwords(item.attrib['v'])   # Assign temporary variable, st_name. Retain item.attrib['v'] for comparison.
            st_name = format_McMac(st_name)
            st_name = format_SpecialCap(st_name)
            st_name = format_DashCap(st_name)
            st_name = format_Special(st_name)

            # FOR PROBLEMATIC MAPPING TEXT, i.e. SAINT STREET SCREENING
            if is_SaintStreet(st_name):
                g = st1.search(st_name)
                st_name = g.group(1) + "St." + mapName(g.group(3))
            else:
                st_name = mapName(st_name)
            # COMPARE BEFORE AND AFTER CHANGE
            check_Diff(item.attrib['v'], st_name, element)
            item.set('v', st_name)

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

k = 1 # Parameter: take every k-th top level element

'''
# SCRIPT #5 (Dry Run)
for i, element in enumerate(get_element(XMLFILE)):
    #  Check every kth top level element
    if i % k == 0:
        format_and_map(element)
''' 

# SCRIPT #6 (Actual Run)
with open("_temp/temp.xml", 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n ')
    for i, element in enumerate(get_element(XMLFILE)):
        #  Check every kth top level element
        if i % k == 0:
            format_and_map(element)
            output.write(ET.tostring(element, encoding='utf-8'))
    output.write('</osm>')

from shutil import move
move("_temp/temp.xml", XMLFILE)



"""
Script #2
1. Run this script to check for inconsistent street names:
      $ python 2_screen.py > Logs/Inconsistent_Entries.log

2. Check the log of inconsistent entries to see if there are valid street names that slipped through.

3. Valid street names that do not pass the consistency check can be filtered out
  - enter the street name in SCREENED in the 'Lists/' folder.

4. Re-run this script after SCREENED is updated.

5. FOLLOW-UP:
- Make a copy of the files in problem entries and place them in the 'Corrected_Entries/' folder.
- Update the problem entries with the correct information, fields, etc.
- Mark the corresponding INDEX entry of a document/element that is intended to be dropped from the XML dataset.
The marking is to be done in the INDEX file.

"""

# PACKAGES
import string
import re
import xml.etree.cElementTree as ET
from helperFunctions import getList
from os import remove, listdir
import glob

# FILE PATH
path = "../Dataset/"
filename = "singapore.xml"
XMLFILE = path + filename

# REGEX MATCHING (Use re.search and re-assemble the groups, after formatting)
ic0 = re.compile("(^|.*\s)[a-zA-Z].*\s[a-zA-Z].*") # Inconsistent form #0: Incomplete streetname
ic1 = re.compile(".*[0-9]?[#-][0-9].*") # Inconsistent form #1: House units #XX-YY or XX-YY
ic2 = re.compile("^[bB][lL][oO]?[cC]?[kK].*") # Inconsistent form #2: Building number Blk XX
ic3 = re.compile("^[0-9].*") # Inconsistent form #3: Building/house number XX or postcode
ic4 = re.compile(".*[sS]ingapore.*") # Inconsistent form #4: Not a street

# PREP WORK
file_list = []
SCREENED = getList("Lists/SCREENED")

existing_files = glob.glob("Problem_Entries/*")
for f in existing_files:
    remove(f)

# FUNCTIONS
def is_street_name(elem):
    try:
        return (elem.attrib['k'] == "addr:street")
    except:
        return False

def is_Consistent(street_name):
    t0 = ic0.match(street_name) is not None
    t1 = ic1.match(street_name) is None
    t2 = ic2.match(street_name) is None
    t3 = ic3.match(street_name) is None
    t4 = ic4.match(street_name) is None
    return all([t0, t1, t2, t3, t4])

def check_Consistency(element):
    # YOUR CODE HERE
    for item in element:
        if is_street_name(item):
            st_name = item.attrib['v']            
            if not(is_Consistent(st_name)) and st_name not in SCREENED:
                tagfile = element.tag + element.get('id')
                f = open("Problem_Entries/" + tagfile,"wb")
                f.write(ET.tostring(element, encoding="utf-8"))
                f.close()
                file_list.append(tagfile)
                print "(ID: %s, Type: %s) %s" % (element.attrib['id'], element.tag, st_name)

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

for i, element in enumerate(get_element(XMLFILE)):
    #  Check every kth top level element
    if i % k == 0:
        check_Consistency(element)

fileid = "Problem_Entries/INDEX"
f2 = open(fileid, "wb")
for item in file_list:
    f2.write(item +"\n") 
f2.close()



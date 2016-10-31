"""
Script #4
1. Run this script to  help refine the dictionary of MAPPING texts:
      $ python 4_audit.py > Logs/Audit.log

The MAPPING dictionary is used in Script #6 where the actual data-cleaning takes place. 
The XML dataset is finalized with the modified entries when Script #6 is run.
Running this script will not alter the XML file.

2. Review Audit.log to get a sense of what street types are used in the street name entries.
    - For each street type that appear more than once, 
    enter the proper form of the street type in EXPECTED.

    - For entries whose street type is improper form, or the entry has typo errors, 
    enter the improper form/typo error with its corresponding correction in MAPPING.

    - For valid street names or street types that appear only once in the set, 
    and deciding what street type to enter in EXPECTED is getting tedious or difficult,
    enter the street name entry in SCREENED.

3. If needed, re-run this script as long as there are items to update in the EXPECTED, MAPPING and SCREENED list or dictionary.

4. Go to the next script when the review of the Audit.log is satisfied.

"""

# PACKAGES
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
from helperFunctions import getList, getDict

# FILE PATH
path = "../Dataset/"
filename = "singapore.xml"

XMLFILE = path + filename


# PREP WORK
EXPECTED = getList("Lists/EXPECTED")
SCREENED = getList("Lists/SCREENED")
MAPPING = getDict("Lists/MAPPING")

# FUNCTIONS
def audit_street_type(street_types, street_name):
    ### Street type can typically be the first word or the last word in a street name, but 
    ### street names can end with numbers or alphabets too.

    # Split the string up into a list so that each text segment can be checked.
    names = street_name.split()

    # Filter out street names that have been screened already.
    if names and (street_name not in SCREENED):
        # If any name segment is in the EXPECTED list, the street type is already collected.
        if not any([name in EXPECTED for name in names]):
            # Get the likely street type from first segment and enter into dictionary
            street_types[names[0]].add(street_name)
            # Check if last segment of the street name is a digit. If so, check the segment
            # before that.
            if names[-1].isdigit():
                try:
                    if (names[-2] != names[0]):
                        street_types[names[-2]].add(street_name)
                except:
                    pass
            ### Get the likely street type from last word and enter into dictionary unless
            ### there is only one word in the street name.
            elif names[-1] != names[0]:
                street_types[names[-1]].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(xmlfile):
    file = open(xmlfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    file.close()
    return street_types

def update_name(name, mapping):
    # YOUR CODE HERE
    m = name.split()
    for item in m:
        if item in mapping.keys():
            name = re.sub(item, mapping[item], name)
    return name

# MAIN SCRIPT
def test():
    st_types = audit(XMLFILE)
    pprint.pprint(dict(st_types))
    
    print "\n****************\n"

    streets = set()
    for ways in st_types.itervalues():
        for name in ways:
            streets.add(name)
    
    for name in streets:
        better_name = update_name(name, MAPPING)
        print name, "=>", better_name

if __name__ == '__main__':
    test()

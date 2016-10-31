"""
This script is used to check problematic entries by the street name.
    $ python S_check_by_StreetName.py

Preparatory work:
Store the street name in a file CHECK_STREETNAMES and place it in the folder '_temp/'.

"""

# PACKAGES
import xml.etree.cElementTree as ET

from helperFunctions import getList, getDict

# FILE PATH
path = "../Dataset/"
filename = "singapore.xml"

XMLFILE = path + filename

# PREP WORK
STREETNAMES = getList("_temp/CHECK_STREETNAMES")

# FUNCTIONS
def is_street_name(element):
    try:
        return (element.attrib['k'] == "addr:street")
    except:
        pass

def get_Entry(xmlfile):
    file_list = []
    
    for event, element in ET.iterparse(xmlfile, events=("end",)):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    if (tag.get('v') in STREETNAMES):
                        tagfile = element.tag + element.get('id')
                        f = open("_temp/" + tagfile,"wb")
                        f.write(ET.tostring(element, encoding="utf-8"))
                        f.close()
                        file_list.append(tagfile)
    fileid = "_temp/INDEX"
    f2 = open(fileid, "wb")
    for item in file_list:
        f2.write(item +"\n") 
    f2.close()


# MAIN SCRIPT
def test():
    get_Entry(XMLFILE)

if __name__ == '__main__':
    test()

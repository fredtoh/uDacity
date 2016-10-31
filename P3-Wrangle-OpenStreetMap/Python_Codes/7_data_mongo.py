#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""

path = "../Dataset/"
filename = "singapore.xml"

XMLFILE = path + filename

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        
        ### HELPER FUNCTIONS
        ### get texts before and after colon
        def getTextWithColon(string):
            beforeColon = string[0:string.find(":")]
            afterColon = string[string.find(":")+1:]
            return beforeColon, afterColon
        
        node['type'] = element.tag
        address = {}
        node_refs = []
        node['created'] = {}
        ### We know each element may have child "nodes" we need to extract the attributes
        ### from . Iterate through the parent + children elements.
        for elem in element.iter():            
            tag = elem.tag
            attributes = elem.attrib
            
            if tag == 'tag':
                if lower.search(attributes['k']):
                    node[attributes['k']] = attributes['v']
                if lower_colon.search(attributes['k']):                    
                    before, after = getTextWithColon(attributes['k'])
                    if before == 'addr':
                        address[after] = attributes['v']
                    else:
                        keyName = before + '_' + after
                        node[keyName] = attributes['v']
                if problemchars.search(attributes['k']):                                
                    pass

            if tag == 'nd':
                node_refs.append(attributes['ref'])

            if tag == 'way':
                for key in attributes:
                    if key in CREATED:
                        node['created'].update({key: attributes[key]})
                    else:
                        node[key] = attributes[key]

            if tag == 'node':
                pos = [float(attributes['lat']), float(attributes['lon'])]
                node['pos'] = pos
                for key in attributes:
                    if key in CREATED:
                        node['created'].update({key: attributes[key]})
                    elif key not in ['lat','lon']:
                        node[key] = attributes[key]

        if element.tag == "way":
            node['node_refs'] = node_refs
        
        if address !={}:
            node['address'] = address

        return node
    else:
        return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map(XMLFILE)
    #pprint.pprint(data)
    
if __name__ == "__main__":
    test()
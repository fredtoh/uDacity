# P3 - DATA WRANGLING PROJECT
## OPEN STREETMAP (OSM): SINGAPORE

## 0. AN OVERVIEW OF SINGAPORE

Singapore is a multi-racial and multi-cultural nation with a population of around 4 million, located in Southeast Asia. It is an island city-state,   occupying merely 278 square miles of land area, which makes it one of the most densely-populated nation in the world.

I chose Singapore for this project because I grew up there. With my familiarity with this area, I thought the exploration using MongoDB will be very interesting and exciting. I downloaded the OSM file by sending the following web query:
`http://overpass-api.de/api/map?bbox=103.6691,1.2000,104.0817,1.4253` 

## <a name="street-name-format"></a>1. STREET NAME FORMAT

I noticed several problems with the data regarding street names as I began with  sampling the OSM file of Singapore. Before I go on to describe the problems I have encountered, I think it would be appropriate to briefly mention the typical format of a street name in Singapore:

* _Proper Name_, followed by the _**Street Type**_ (e.g. _MacKenzie **Road**_)
* _**Street Type**_, followed by the _Proper Name_ (e.g. _**Lorong** Ah Soo_)

Numerals *(and occasionally an alphabet)* may follow after the street type, (e.g. _Hougang Street **51**_). These names indicate that there are more than one branches bearing the same street name.

These two formats display the multi-cultural aspect of Singapore. The first format not only reflects the modern day Singapore as an English-speaking nation, but also its colonial history under the British rule between the years 1819 and 1942. The second format reflects its rich Malayan heritage. The three most common street types associated with the second format from the dataset are: _Jalan_ (which translates to 'street' in English), _Lorong_ ('lane') and _Taman_ ('park'). Others include _Kampong_, _Lengkong_ and _Bahru_.

<div style="page-break-after: always;"></div>
## 2. PROBELMS ENCOUNTERED

The problems I have encountered during the data-cleaning process include: 

* Entries inconsistent with the accepted formats 
* Problematic mapping text 
* Formatting atypical names

Elaborations on these problems follow next.

### Inconsistent Formats

There are 39 documents whose street name entries have shown inconsistency from the expected format. They are broadly categorized by:

* The entry is incomplete.
  * (e.g. _Street 81_)
* The entry contains the house or building number.
  * (e.g. _**1013** Geylang East Ave 3_, _**Blk 10** Ubi Crescent_)
* The entry contains the house unit.
  * (e.g. _East Coast Road **#03-09**_)
* The entry is not a street name.
  * (e.g. _310074_, _656289_, _Park Regis Singapore_)

I use regular expressions (regex) to screen for inconsistent street names, and below are code snippets describing the regex:

```python
import re

# Inconsistent form #0: Incomplete streetname. 
# At least two groups expected: Proper Name, Street Type
ic0 = re.compile("(^|.*\s)[a-zA-Z].*\s[a-zA-Z].*") 

# Inconsistent form #1: House units #XX-YY or XX-YY
ic1 = re.compile(".*[0-9]?[#-][0-9].*") 

# Inconsistent form #2: Building number Blk XX
ic2 = re.compile("^[bB][lL][oO]?[cC]?[kK].*") 

# Inconsistent form #3: Building/house number XX or postcode (Not a street name)
ic3 = re.compile("^[0-9].*") 

# Inconsistent form #4: Not likely a street name if "Singapore" is in the entry
ic4 = re.compile(".*[sS]ingapore.*") 

```

Hence I create a function that returns `True` if a street name entry within a document is consistent with the expected format.

```python
# Function to check for consistency
def is_Consistent(street_name):
    t0 = ic0.match(street_name) is not None
    t1 = ic1.match(street_name) is None
    t2 = ic2.match(street_name) is None
    t3 = ic3.match(street_name) is None
    t4 = ic4.match(street_name) is None

    # Return True or False
    return all([t0, t1, t2, t3, t4])
```

Unfortunately, another problem surfaced when I use this function. I discovered several documents bear the street name _Queensway_, which is entirely valid. This special case requires me create a new variable called **SCREENED** to exclude valid entries from the consistency check.

Cleaning the problematic entries programatically would be difficult. So I have chosen to, via python scripting, clean these entries "manually" with the following strategy:

1. (Python) Extract the parent xml element whose `addr:street` entry is tested inconsistent. Element is saved to a text file.  
_To make the process programmatically easy, the filenames are uniquely identified by the "tag type" followed by the "element ID". I also create another file named **INDEX** to store those filenames in a list._
2. (Manual) Update each text file with the correct information.  
  - If street name is missing or incomplete, check for clues via the parent element (e.g. if website is available, check for address there, or carry out a web search for address if possible.)
  - Look for the `pos` field value, which contains the latitude and longitude information. Validate that against google maps, which is my gold standard choice.
  - If the location and the address information do not corroborate, mark the problem filename entry in **INDEX** by prefixing it with "***", say.
3. (Python) When the "tag type" and the "element ID" match up with the list of filenames in **INDEX**, the python script will upload the contents of the matching file and replace the parent xml element. If matched to the marked filename, the parent element will be skipped over and not stored.

As a result, the element that has the street name entry _Street 81_ is dropped because it dose not contain sufficient address information.

### <a name="problem-map"></a>Problematic Mapping Text

In this dataset, _St_ and _St._ are the only problematic ones. Since _St_ and _St._ are also the mapping texts for "Street", it would be disastrous for original entries such as _St Andrew's Road_ or _St. George's Lane_. The mapped entries would have been changed to _**Street** Andrew's Road_ or _**Street** George's Lane_.

The resolution I have sought for this particular problem is laid out in the [**"Saint" streets**](#saint-streets) segment.

### Formatting Atypical Names

I face with additional challenges for the following situation:

* Special capitalization
  - Capital letter after "Mc" or "Mac" (e.g. _McNally Street_)
  - Capital letter after the apostrophe (e.g. _D'Almeida Street_)
  - Capital letter after the dash (e.g. _One-North Gateway_)
* "Saint" streets (e.g. _St. Andrew's Road_, _St. George's Lane_)

<div style="page-break-after: always;"></div>
###### Special Capitalization

For street name capitalization, I typically would just use `string.capwords()`. 

```python
import string

string.capwords(st_name) # st_name is the street name entry
```

But there are entries that do not follow the typical capitalization rules. So I turn to regex for those special cases to make sure the capital letters are showing up correctly in the street name entries. Below are the code snippets for the case of "Mc" and "Mac" names:

```python
# Regex to match 'Mc' and 'Mac' street names
cap1 = re.compile("(^|.*\s)([mM]a?c)(.*)") 

# Formatting function
def format_McMac(street_name):
    g = cap1.search(street_name)
    if g is not None:
        return g.group(1) + string.capwords(g.group(2)) + string.capwords(g.group(3))
    else:
        return street_name
```
In similar fashion, I do the same for the other special cases. Below are the regex for them:

```python
# Regex for other special capitalization
cap2 = re.compile("(^|.*\s)([dolDOL]')(.*)") # After D', O' or L'
cap3 = re.compile("(.*[a-z]-)([a-zA-Z].*)") # After dash
```

###### <a name="saint-streets"></a>"Saint" Streets

I have chosen to use "St." as the proper form because the non-abbreviated form, "Saint", is somewhat an awkward representation. But as mentioned [earlier](#problem-map), "St." is in conflict with the mapping text for "Street". 

The solution is simple. Instead of passing the whole street name entry to the mapping function, `mapName()`, I pass only the text that comes after "St." for mapping. The replacement of "St." to "Street" is thus avoided.

```python
# Regex for "Saint" streets
st1 = re.compile("(^|.*\s)([sS]t.?|[sS]aint)(\s[A-Za-z].*)")

# Function to check street name
def is_SaintStreet(street_name):
    return st1.match(street_name) is not None

# Here, st_name is the street name entry. 
# (Code is not displayed where ... is shown.) 
...
	if is_SaintSt(st_name):
	    g = st1.search(st_name)
	    st_name = g.group(1) + "St." + mapName(g.group(3))
	else:
	    # Mapping the whole street name entry
	    st_name = mapName(st_name)    
...
    
```

## 3. DATA OVERVIEW

This section contains basic statistics about the dataset and the MongoDB queries used to gather them. Here are some information regarding the data files:

Filename | Size  | Comments
---|---|---
singapore.osm | 145.7 MB  | The original OSM file
singapore.xml | 147.4 MB  | XML format (Cleaned)
singapore.xml.json | 159.3 MB | JSON format (MongoDB-ready)

The database is stored to *osm* under the collection *sgp*.

```bash
$ mongoimport -d osm -c sgp --file sinagpore.xml.json
```

<div style="page-break-after: always;"></div>
### Queries
###### Number of documents
```mongo
> db.sgp.find().count()                                                
725540
```
###### Number of nodes  
```mongo
> db.sgp.find({"type":"node"}).count()
636204
```
###### Number of ways 
```mongo                                                
> db.sgp.find({"type":"way"}).count()
89300
```
###### Number of unique users
```mongo                                                
> db.sgp.distinct("created.user").length
1087
```
###### Number of unique amenity types
```mongo                                                
> db.sgp.distinct("amenity").length
96
```
<div style="page-break-after: always;"></div>
###### Top 10 amentities by count
```mongo                                                
> db.sgp.aggregate([{"$match":{"amenity":{"$exists":1}}}, 
... {"$group":{"_id":"$amenity","count":{"$sum":1}}}, 
... {"$sort":{"count":-1}}, 
... {"$limit":10}])
{ "_id" : "parking", "count" : 1623 }
{ "_id" : "restaurant", "count" : 974 }
{ "_id" : "school", "count" : 437 }
{ "_id" : "taxi", "count" : 314 }
{ "_id" : "place_of_worship", "count" : 281 }
{ "_id" : "swimming_pool", "count" : 263 }
{ "_id" : "cafe", "count" : 249 }
{ "_id" : "fast_food", "count" : 211 }
{ "_id" : "toilets", "count" : 171 }
{ "_id" : "fuel", "count" : 166 }

```

## 4. ADDITIONAL IDEA

I want to explore the geospatial feature of MongoDB. The question I have in my mind is this: _What amenities are nearby my former middle school?_

First, I want to inspect the information that the document has on my former middle school, _Victoria School_. I am storing the query result to a variable

```mongo
> var vs = db.sgp.find({"name":"Victoria School"}).toArray()
> vs[0]
{
	"_id" : ObjectId("58174da74ed0b226097a0215"),
	"name" : "Victoria School",
	"asset_ref" : "93201",
	"created" : {
		"changeset" : "36529447",
		"user" : "JaLooNz",
		"version" : "7",
		"uid" : "741163",
		"timestamp" : "2016-01-12T14:03:11Z"
	},
	"pos" : [
		1.3092614,
		103.9278707
	],
	"route_ref" : "31;36;43;47;48;55;135;155;196;196e;197;401",
	"location" : "Marine Parade Road",
	"type" : "node",
	"id" : "410467565",
	"highway" : "bus_stop"
}
```

As a side note, I see that this record has neither an `"address"` nor an `"amenity"` field. It has the field `"location"` which could have been an `"address.street"` field instead. Also, I must admit I do not fully understand the purpose of having a `"highway"` field that holds the value of "bus\_stop" in this record.

### Geospatial Feature

From MongoDB documentation, I gather that I should index the `"pos"` field with the parameter `"2d"`. Then I can use the `"$near"` operator to perform proximity search. 

<div style="page-break-after: always;"></div>
###### Creating geospatial index on the 'pos' field.
```mongo
> db.sgp.ensureIndex({"pos": "2d"})
{
	"createdCollectionAutomatically" : false,
	"numIndexesBefore" : 1,
	"numIndexesAfter" : 2,
	"ok" : 1
}
```
Below is the query on amenities near my middle school. I am limiting the query to return two results. 

###### 
```mongo
> db.sgp.find(
...      {"pos": {"$near": vs[0].pos},
...       "amenity": {"$exists": 1}, "address.street":{"$exists": 1}
...      },
...      {"_id":0, "name":1, "pos":1, "amenity": 1, "address.street": 1}
...      ).limit(2).pretty()
{
	"amenity" : "ice_cream",
	"name" : "Ice Cream Chefs",
	"pos" : [
		1.3101987,
		103.9184457
	],
	"address" : {
		"street" : "East Coast Road"
	}
}
{
	"amenity" : "cafe",
	"name" : "Dutch Colony Coffee Co.",
	"pos" : [
		1.314218,
		103.9193777
	],
	"address" : {
		"street" : "Frankel Avenue"
	}
}
```
<div style="page-break-after: always;"></div>
Although I am not familiar with these two establishments, _Ice Cream Chefs_ and _Dutch Colony Coffee Co._, I can vouch that the streets, _East Coast Road_ and _Frankel Avenue_, are pretty close to my school along _Marine Parade Road_.

## 5. CONCLUSION                        

The open street map data for Singapore is no doubt "dirty". For example, when I search for my middle school, its lack of the `"address"` field exhibits the lack of completeness in the dataset. 

On the other hand, I learn this is where a NoSQL database with a dynamic schema, like MongoDB, shows its strength. It means that I am not required to ensure the records/documents conform to a strict, pre-defined schema when creating the database. For me, it means I could avoid the organizational nightmare of creating tables after tables of data in order to build a relational database that works. But as I learn from MongoDB documentation, in the realm of agile development, where the schema of the database changes frequently and fast, a NoSQL database triumphs over relational database in terms of speed and reliability.


## REFERENCES

1. Web Query. In _Overpass-API_. Retrieved September 12, 2016, from <http://overpass-api.de/api/map?bbox=103.6691,1.2000,104.0817,1.4253>

2. History of the Reuplic of Singapore. In _Wikipedia._ Retrieved October 31, 2016, from <https://en.wikipedia.org/wiki/History_of_the_Republic_of_Singapore>

3. Create a 2d Index. In _MongoDB_. Retrieved October 28, 2016, from <https://docs.mongodb.com/v3.2/tutorial/build-a-2d-index/>

4. NoSQL Databases Explained. In _MongoDB_. Retrieved October 29, 2016, from <https://www.mongodb.com/nosql-explained>

5. Agile Development. In _MongoDB_. Retrieved October 29, 2016, from <https://www.mongodb.com/agile-development>
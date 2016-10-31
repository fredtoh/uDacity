# PYTHON CODES

There are 7 main scripts for this project:

* Script #1:   `1_output_xml.py`
* Script #2:   `2_screen.py`
* Script #3:   `3_update_problem_entries.py`
* Script #4:   `4_audit.py`
* Script #5:   `5_mapping_dryrun.py`
* Script #6:   `6_clean_data.py`
* Script #7:   `7_data_mongo.py`

1. Run this script to convert the original, dirty OSM file to an XML file for further cleaning.
`      $ python 1_output_xml.py`

2. Run Script #2 to filter out inconsistent street name entries. 
Go to the script for instructions. Re-running this script a couple of times may be needed.

3. Run Script #3 only when all the problem entries are corrected. Run this ONLY ONCE.
If data quality has not been achieved downstream due to inconsistent entries, 
restart the data-cleaning process from Script #2.

4. Run Script #4 to help with refining the dictionary of MAPPING texts necessary to clean the dataset.
Go to the script for instructions. Re-running this script several times may not be necessary.

5. Run Script #5 to review the data-cleaning as a dry run. 
Decisions to improve on the modification of entries are still allowed after running Script #5.
Modifying and re-running this script several times may be necessary.

6. Run Script #6 ONLY ONCE.
The XML file will be finalized with any modified entries after this script is run.
If data quality still has not been achieved after running Script #6, it may be necessary to 
revisit what is done in Scripts #2-#5.

7. Review the cleaned XML file for new data quality problems that could have surfaced:
   - Copy the scripts and contents of previous round of \_temp, logs, lists, problem entries, corrected entries into the '_old' folder.
   Place in an indexed folder which will help identify the number of rounds of data-cleaning that had taken place.
   - Re-run Scripts #2-#6.
   - Review that the logs.
   - Repeat this step (Step 7) as long as the logs are not empty.

8. Run Script #7 only once.
The output of Script #7 is the MongoDB-ready JSON file. 
To load the database, use the following command in shell, 
`      $ mongoimport -d osm -c sgp --file ../Dataset/singapore.xml.json`

9. To review a set of cleaned up street names, do the following in shell / mongo:

```
      $ mongo osm << EOF > streetnames.txt    #Entering the mongo shell next
      > db.sgp.distinct("address.street").length
      > db.sgp.distinct("address.street").sort()
      > EOF
```

NOTES:
If data quality has not been achieved downstream due to inconsistent entries, 
restart the data-cleaning process from Script #2.

If data quality has not been achieved downstream due to non-uniform street types,
restart from Script #4.

If data quality has not been achieved downstream due to inaccurate information,
use the `S_check_by_StreetName.py` script. Go to the script for instructions.

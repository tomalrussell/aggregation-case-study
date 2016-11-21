
# Download OpenStreetMap extract for Norfolk
data/norfolk-latest.osm.pbf:
	wget -P ./data http://download.geofabrik.de/europe/great-britain/england/norfolk-latest.osm.pbf

# Download Census statistics
data/KS_QS_OA_UK_V1.zip:
	wget -P ./data http://data.statistics.gov.uk/Census/KS_QS_OA_UK_V1.zip

# Extract Table for Population (and residence type) by Output Area
data/QS101UKDATA.CSV: data/KS_QS_OA_UK_V1.zip
	unzip -p data/KS_QS_OA_UK_V1.zip KS_QS_OA_UK/Data/QS101UKDATA.CSV > data/QS101UKDATA.CSV

# Download Local Authority Districts, Unitary Authorities and Boroughs geography
data/England_lad_2011_clipped.zip:
	wget -P ./data https://census.edina.ac.uk/ukborders/easy_download/prebuilt/shape/England_lad_2011_clipped.zip

# Extract Local Authority Districts, Unitary Authorities and Boroughs geography
data/lad/england_lad_2011_clipped.shp: data/England_lad_2011_clipped.zip
	unzip -d data/lad data/England_lad_2011_clipped.zip

# Download Output Area geography
data/England_oa_2011_clipped.zip:
	wget -P ./data https://census.edina.ac.uk/ukborders/easy_download/prebuilt/shape/England_oa_2011_clipped.zip

# Extract Output Area geography
data/oa/england_oa_2011_clipped.shp: data/England_oa_2011_clipped.zip
	unzip -d data/oa data/England_oa_2011_clipped.zip

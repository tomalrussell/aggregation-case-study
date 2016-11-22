
# Download OpenStreetMap extract for Norfolk
data/norfolk-latest.osm.pbf:
	wget -P ./data http://download.geofabrik.de/europe/great-britain/england/norfolk-latest.osm.pbf

# Extract OpenStreetMap buildings to PostgreSQL database
db_osm_buildings:
	ogr2ogr -f "PostgreSQL" PG:"dbname=tom user=tom" -where "building is not null" data/norfolk-latest.osm.pbf -nlt POLYGON -nln osm_buildings multipolygons

# Extract OpenStreetMap buildings to shapefile
data/osm/norfolk_buildings.shp:
	ogr2ogr -f "ESRI Shapefile" -select "osm_id,name,amenity,building" -where "building is not null" data/osm/norfolk_buildings.shp data/norfolk-latest.osm.pbf -nlt POLYGON -nln osm_buildings -lco "ENCODING=UTF8" multipolygons

# Download Census statistics
data/KS_QS_OA_UK_V1.zip:
	wget -P ./data http://data.statistics.gov.uk/Census/KS_QS_OA_UK_V1.zip

# Extract Table for Population (and residence type) by Output Area
# - extract single file from zip
# - skip first two lines
# - remove thousands separator
data/QS101UKDATA.CSV: data/KS_QS_OA_UK_V1.zip
	unzip -p data/KS_QS_OA_UK_V1.zip KS_QS_OA_UK/Data/QS101UKDATA.CSV | \
	awk 'NR>2' | \
	sed -r 's/"([0-9]+),([0-9]+)"/\1\2/g' \
	> data/QS101UKDATA.CSV

# Download Local Authority Districts, Unitary Authorities and Boroughs geography
data/England_lad_2011_clipped.zip:
	wget -P ./data https://census.edina.ac.uk/ukborders/easy_download/prebuilt/shape/England_lad_2011_clipped.zip

# Extract Local Authority Districts, Unitary Authorities and Boroughs geography
data/lad/england_lad_2011_clipped.shp: data/England_lad_2011_clipped.zip
	unzip -d data/lad data/England_lad_2011_clipped.zip

# Extract Local Authority Districts, Unitary Authorities and Boroughs geography
data/lad/england_lad_2011_clipped_norfolk.shp: data/lad/England_lad_2011_clipped.shp
	ogr2ogr -f "ESRI Shapefile" \
	-where "label in ('E07000143', 'E07000144', 'E07000145', 'E07000146', 'E07000147', 'E07000148', 'E07000149')" \
	data/lad/england_lad_2011_clipped_norfolk.shp data/lad/england_lad_2011_clipped.shp

# Dissolve and buffer a Norfolk outline from a few LADs (selected by ID)
data/norfolk-outline.shp: data/lad/england_lad_2011_clipped.shp
	ogr2ogr -f "ESRI Shapefile" \
	data/norfolk-outline.shp data/lad/england_lad_2011_clipped.shp \
	-dialect sqlite \
	-sql "select ST_union(ST_buffer(Geometry,200)) from england_lad_2011_clipped WHERE label in ('E07000143', 'E07000144', 'E07000145', 'E07000146', 'E07000147', 'E07000148', 'E07000149')"

# Download Output Area geography
data/England_oa_2011_clipped.zip:
	wget -P ./data https://census.edina.ac.uk/ukborders/easy_download/prebuilt/shape/England_oa_2011_clipped.zip

# Extract Output Area geography
data/oa/england_oa_2011_clipped.shp: data/England_oa_2011_clipped.zip
	unzip -d data/oa data/England_oa_2011_clipped.zip

# Join population stats to ouput areas
data/oa/england_oa_2011_clipped_with_pop.shp: data/oa/england_oa_2011_clipped.shp data/QS101UKDATA.CSV data/norfolk-outline.shp
	python join.py

# Download Liverpool OSM metro extract
data/liverpool_england.imposm-shapefiles.zip:
	wget -P ./data https://s3.amazonaws.com/metro-extracts.mapzen.com/liverpool_england.imposm-shapefiles.zip

# Extract Liverpool OSM metro extract
data/osm/liverpool_england_osm_buildings.shp: data/liverpool_england.imposm-shapefiles.zip
	unzip -d data/osm data/liverpool_england.imposm-shapefiles.zip
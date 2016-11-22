"""Script to join output area population data to boundary data
- calculate OA area and population density
- limit to Norfolk
"""
from __future__ import division
import fiona
from shapely.geometry import shape
import csv

# load population counts
records = {}

with open('data/QS101UKDATA.CSV', 'r') as pop_csv:
    r = csv.DictReader(pop_csv)
    for line in r:
        area_id = line['GeographyCode']
        pop = line['All categories: Residence type']
        try:
            records[area_id] = int(pop)
        except ValueError:
            pass

with fiona.drivers():
    # load Norfolk outline
    with fiona.open('data/norfolk-outline.shp') as outline:
        outline_geom = shape(outline[0]['geometry'])

        # load output areas
        with fiona.open('data/oa/england_oa_2011_clipped.shp') as src:
            print("Found {} features".format(len(src)))

            # set up output schema
            sink_schema = src.schema.copy()
            sink_schema['properties']['pop'] = 'int'
            sink_schema['properties']['area'] = 'float'
            sink_schema['properties']['density'] = 'float'

            # Create a sink file to write out features
            with fiona.open(
                    'data/oa/england_oa_2011_clipped_with_pop.shp', 'w',
                    crs=src.crs,
                    driver=src.driver,
                    schema=sink_schema) as sink:

                i = 0
                for feature in src:
                    area_id = feature['properties']['code']

                    # check we have population data
                    if area_id in records:
                        s = shape(feature['geometry'])

                        # check against outline
                        if s.intersects(outline_geom):
                            pop = records[area_id]

                            # write out feature with pop, area and density
                            feature['properties'].update(
                                pop=pop,
                                area=s.area,
                                density=pop/s.area)

                            sink.write(feature)

                    i = i + 1
                    if i % 10000 == 0:
                        print("- checked {} features".format(i))

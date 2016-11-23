from collections import namedtuple
import fiona
from shapely.geometry import shape
from rtree import index

INPUT_GEOMETRY_FILE = 'data/oa/england_oa_2011_clipped_with_pop.shp'
REPORTING_GEOMETRY_FILE = 'data/lad/england_lad_2011_clipped_norfolk.shp'
OUTPUT_FILE = 'data/lad/england_lad_2011_clipped_norfolk_with_pop.shp'
# REPORTING_GEOMETRY_FILE = 'data/grid.shp'
# OUTPUT_FILE = 'data/grid_with_pop.shp'
INITIAL_REPORTING_VALUE = 0
INPUT_ATTRIBUTE_TO_REPORT = 'pop'
INPUT_ATTRIBUTE_TO_REPORT_TYPE = 'float'

input_features = []
idx = index.Index()

def proportion_of_a_intersecting_b(a, b):
    intersection = a.intersection(b)
    return intersection.area / a.area

ShapeWithValue = namedtuple('ShapeWithValue', ['shape', 'value'])

with fiona.drivers():
    with fiona.open(INPUT_GEOMETRY_FILE) as input_src:
        for feature in input_src:
            s = ShapeWithValue(
                shape=shape(feature['geometry']),
                value=feature['properties'][INPUT_ATTRIBUTE_TO_REPORT]
            )
            input_features.append(s)

    # Populate R-tree index with bounds of input features
    for pos, feature in enumerate(input_features):
        idx.insert(pos, feature.shape.bounds)

    with fiona.open(REPORTING_GEOMETRY_FILE) as reporting_src:
        sink_schema = reporting_src.schema.copy()
        sink_schema['properties'][INPUT_ATTRIBUTE_TO_REPORT] = INPUT_ATTRIBUTE_TO_REPORT_TYPE
        sink_schema['properties']['pop_density'] = 'float'

        with fiona.open(
            OUTPUT_FILE, 'w',
            crs=reporting_src.crs,
            driver="ESRI Shapefile",
            schema=sink_schema) as reporting_sink:

            for reporting_feature in reporting_src:
                reporting_shape = shape(reporting_feature['geometry'])
                reporting_value = INITIAL_REPORTING_VALUE

                # look up bbox intersecting features in R-tree
                intersecting_features = [input_features[pos] for pos in idx.intersection(reporting_shape.bounds)]

                for input_feature in intersecting_features:
                    # find proportion of input feature that intersects
                    input_shape = input_feature.shape
                    proportion = proportion_of_a_intersecting_b(input_shape, reporting_shape)
                    # add that proportion of the attribute_to_report to the reporting_value
                    reporting_value = reporting_value + proportion * input_feature.value

                print(reporting_value)
                reporting_feature['properties'][INPUT_ATTRIBUTE_TO_REPORT] = reporting_value
                reporting_feature['properties']['pop_density'] = reporting_value / reporting_shape.area

                reporting_sink.write(reporting_feature)


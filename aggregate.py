from __future__ import print_function
import argparse
from collections import namedtuple
import fiona
from shapely.geometry import shape
from rtree import index

def proportion_of_a_intersecting_b(a, b):
    intersection = a.intersection(b)
    return intersection.area / a.area

ShapeWithValue = namedtuple('ShapeWithValue', ['shape', 'value'])

def aggregate(input_file, output_file, reporting_geometry, reporting_initial_value, reporting_attribute, reporting_attribute_type):
    input_features = []
    idx = index.Index()

    with fiona.drivers():
        with fiona.open(input_file) as input_src:
            for feature in input_src:
                s = ShapeWithValue(
                    shape=shape(feature['geometry']),
                    value=feature['properties'][reporting_attribute]
                )
                input_features.append(s)

        # Populate R-tree index with bounds of input features
        for pos, feature in enumerate(input_features):
            idx.insert(pos, feature.shape.bounds)

        with fiona.open(reporting_geometry) as reporting_src:
            sink_schema = reporting_src.schema.copy()
            sink_schema['properties'][reporting_attribute] = reporting_attribute_type

            with fiona.open(
                output_file, 'w',
                crs=reporting_src.crs,
                driver="ESRI Shapefile",
                schema=sink_schema) as reporting_sink:

                for reporting_feature in reporting_src:
                    reporting_shape = shape(reporting_feature['geometry'])
                    reporting_value = reporting_initial_value

                    # look up bbox intersecting features in R-tree
                    intersecting_features = [input_features[pos] for pos in idx.intersection(reporting_shape.bounds)]

                    for input_feature in intersecting_features:
                        # find proportion of input feature that intersects
                        input_shape = input_feature.shape
                        proportion = proportion_of_a_intersecting_b(input_shape, reporting_shape)
                        # add that proportion of the attribute_to_report to the reporting_value
                        reporting_value = reporting_value + proportion * input_feature.value

                    print(reporting_value)
                    reporting_feature['properties'][reporting_attribute] = reporting_value

                    reporting_sink.write(reporting_feature)

def setup_parser():
    """Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Aggregate a value from one geometry to another.')

    parser.add_argument('-i', '--input-file',
        required=True,
        help='Path to the input file, containing the data to be aggregated.')
    parser.add_argument('-o', '--output-file',
        required=True,
        help='Path to the output file.')
    parser.add_argument('-rg', '--reporting-geometry',
        required=True,
        help='Path to the reporting geometry file, containing geometry to be used as output.')
    parser.add_argument('-ri', '--reporting-initial-value',
        required=True,
        help='Initial value for the attribute to output (used if no geometries intersect)')
    parser.add_argument('-ra', '--reporting-attribute',
        required=True,
        help='Attribute name')
    parser.add_argument('-rt', '--reporting-attribute-type',
        required=True,
        choices=['int', 'str', 'float'],
        help='Type of value (can be "int", "str" or "float")')

    parsed_args = parser.parse_args()

    if parsed_args.reporting_attribute_type == 'int':
        parsed_args.reporting_initial_value = int(parsed_args.reporting_initial_value)

    if parsed_args.reporting_attribute_type == 'str':
        parsed_args.reporting_initial_value = str(parsed_args.reporting_initial_value)

    if parsed_args.reporting_attribute_type == 'float':
        parsed_args.reporting_initial_value = float(parsed_args.reporting_initial_value)

    return parsed_args


if __name__ == '__main__':
    args = setup_parser()

    """Example usage:

    python aggregate.py \
      -i  data/oa/england_oa_2011_clipped_with_pop.shp \
      -o  data/grid_with_pop.shp \
      -rg data/grid.shp \
      -ri 0 -ra pop -rt int
    """
    aggregate(
        args.input_file,
        args.output_file,
        args.reporting_geometry,
        args.reporting_initial_value,
        args.reporting_attribute,
        args.reporting_attribute_type
    )

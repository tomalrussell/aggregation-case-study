"""Script to generate a grid of square cells
- set constants to define bounding box, cell size and CRS
"""
import fiona
from fiona.crs import from_epsg
from shapely.geometry import box, mapping

GRID_BBOX = (540000, 272000, 650000, 347000)
CELL_WIDTH = 10000
CELL_HEIGHT = 10000
CRS_EPSG_CODE = 27700

with fiona.drivers():
    sink_schema = {
        "geometry": "Polygon",
        "properties": {}
    }

    # Create a sink file to write out features
    with fiona.open(
            'data/grid.shp', 'w',
            crs=from_epsg(CRS_EPSG_CODE),
            driver="ESRI Shapefile",
            schema=sink_schema) as sink:

        current_x = GRID_BBOX[0]

        # create grid of square cells,
        # possibly over-running the GRID_BBOX at the xmax/ymax edges
        while current_x <= GRID_BBOX[2]:
            current_y = GRID_BBOX[1]

            while current_y <= GRID_BBOX[3]:
                cell = box(
                    current_x,
                    current_y,
                    current_x + CELL_WIDTH,
                    current_y + CELL_HEIGHT
                )

                sink.write({
                    "geometry": mapping(cell),
                    "properties": {}
                })

                current_y = current_y + CELL_HEIGHT

            current_x = current_x + CELL_WIDTH

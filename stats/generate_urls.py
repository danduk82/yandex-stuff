#!/bin/env python3

import argparse
import random
from math import floor
from owslib.wmts import WebMapTileService

def generate_random_tile_url(capabilities_url, layer, tilematrixset, level, bbox):
    """
    Generate a random WMTS tile URL within a given BBOX.
    
    Parameters:
      capabilities_url (str): URL (or file path) to the WMTS GetCapabilities document.
      layer (str): The WMTS layer name.
      tilematrixset (str): The identifier of the tile matrix set (e.g., "GoogleMapsCompatible").
      level (str): The tile matrix level (as defined in the capabilities, e.g., "10").
      bbox (tuple): Bounding box in the same SRS as the tilematrixset (minx, miny, maxx, maxy).
      
    Returns:
      str: A tile URL with randomly selected tile column and row that intersect the BBOX.
    """
    # Parse the WMTS capabilities document
    wmts = WebMapTileService(capabilities_url)
    
    # Get the tile matrix definitions for the specified tile matrix set.
    tile_matrices = wmts.tilematrixsets[tilematrixset].tilematrix
    
    if level not in tile_matrices:
        raise ValueError(f"Tile matrix level {level} not found in the tile matrix set {tilematrixset}.")
    
    matrix = tile_matrices[level]
    
    # Extract properties from the tile matrix:
    tile_width = matrix.tilewidth           # in pixels
    tile_height = matrix.tileheight         # in pixels
    topLeft = matrix.topleftcorner          # typically (minx, maxy)
    scale_denom = matrix.scaledenominator
    
    # WMTS spec uses a pixel size of 0.28 mm.
    # Resolution (map units per pixel) is computed as:
    resolution = scale_denom * 0.00028  # e.g., meters per pixel if the SRS is in meters
    
    # Compute tile width/height in map units:
    tileWidthMapUnits = tile_width * resolution
    tileHeightMapUnits = tile_height * resolution
    
    # Unpack the BBOX (assumed to be in the same SRS as the tilematrixset)
    minx, miny, maxx, maxy = bbox
    
    # Calculate tile column (x) and row (y) indices that cover the BBOX.
    # For tile columns, the formula is:
    #   tilecol = floor((x - topLeftX) / tileWidthMapUnits)
    tilecol_min = int(floor((minx - topLeft[0]) / tileWidthMapUnits))
    tilecol_max = int(floor((maxx - topLeft[0]) / tileWidthMapUnits))
    
    # For tile rows, since the topLeft y is the maximum,
    #   tilerow = floor((topLeftY - y) / tileHeightMapUnits)
    tilerow_min = int(floor((topLeft[1] - maxy) / tileHeightMapUnits))
    tilerow_max = int(floor((topLeft[1] - miny) / tileHeightMapUnits))
    
    # Ensure the indices fall within the defined matrix dimensions:
    matrix_width = matrix.matrixwidth
    matrix_height = matrix.matrixheight
    
    tilecol_min = max(tilecol_min, 0)
    tilecol_max = min(tilecol_max, matrix_width - 1)
    tilerow_min = max(tilerow_min, 0)
    tilerow_max = min(tilerow_max, matrix_height - 1)
    
    if tilecol_min > tilecol_max or tilerow_min > tilerow_max:
        raise ValueError("BBOX does not intersect with the tile matrix extent.")
    
    # Pick random tile indices within the BBOX range
    tilecol = random.randint(tilecol_min, tilecol_max)
    tilerow = random.randint(tilerow_min, tilerow_max)
    
    # Use the WMTS object to generate the tile URL.
    # (Note: Depending on the capabilities, this may use a ResourceURL template.)
    tile_url = wmts.buildTileRequest(layer=layer,
                               tilematrixset=tilematrixset,
                               tilematrix=level,
                               column=tilecol,
                               row=tilerow)
    return tile_url

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate a random WMTS tile URL within a given BBOX."
    )
    parser.add_argument(
        "--base_url",
        type=str,
        default="/geoserver/gwc/service/wmts",
        help="WMTS GetCapabilities URL."
    )
    parser.add_argument(
        "--layer",
        type=str,
        default="neoc_basics:haltestellenoev3857",
        help="WMTS layer name."
    )
    parser.add_argument(
        "--tilematrixset",
        type=str,
        default="EPSG:3857",
        help="Tile Matrix Set identifier."
    )
    parser.add_argument(
        "--level",
        type=str,
        default="EPSG:3857:15",
        help="Tile Matrix level."
    )
    parser.add_argument(
        "--bbox",
        type=str,
        default="710000, 5831900, 1108800, 6003600",
        help="Bounding box as comma-separated values: minx,miny,maxx,maxy."
    )
    parser.add_argument(
        "--httphost",
        type=str,
        default="https://georchestra-127-0-1-1.traefik.me",
        help="HTTP host for the tile server."
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=10,
        help="Number of random tile URLs to generate."
    )
    
    args = parser.parse_args()
    
    capabilities_url = f"{args.httphost}{args.base_url}?SERVICE=wmts&REQUEST=GetCapabilities"
    
    # Parse bbox from comma-separated string to tuple of floats
    bbox_values = args.bbox.split(',')
    if len(bbox_values) != 4:
        raise ValueError("bbox must have exactly 4 comma separated values: minx,miny,maxx,maxy")
    bbox = tuple(float(val.strip()) for val in bbox_values)
    
    urls = []
    for i in range(args.count):
        url = "{}{}?{}".format(args.httphost, args.base_url, generate_random_tile_url(capabilities_url, args.layer, args.tilematrixset, args.level, bbox))
        
        urls.append(url)
        print(url)
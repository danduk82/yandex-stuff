#!/bin/env python

import random
import argparse as ap
import sys

CH_BBOX_WEBMERCATOR = (710000, 5831900, 1108800, 6003600)

def compute_request_bbox(height, width, center, resolution):
    """
    Compute the bounding box of a WMS request given the center and the scale
    """
    # Compute the half width and half height
    hw = width * resolution / 2
    hh = height * resolution / 2
    # Compute the bounding box
    bbox = (center[0] - hw, center[1] - hh, center[0] + hw, center[1] + hh)
    return bbox

def compute_request_center(bbox):
    """
    Compute the center of a WMS request in a random point inside the bounding box
    """
    min_x, min_y, max_x, max_y = bbox
    # Generate a random x coordinate between min_x and max_x
    center = [random.uniform(min_x, max_x) , random.uniform(min_y, max_y)]
    return center

def generate_wms_urls(bbox, base_url, width, height, nb_urls, layer, crs, format_options):
    
    url_fmt = "{base}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image/png&TRANSPARENT=true&CRS={crs}&STYLES=&FORMAT_OPTIONS={format_options}&WIDTH={width}&HEIGHT={height}&BBOX={bbox}&LAYERS={layernames}"
    
    urls = []
    for i in range(nb_urls):
        resolution = random.uniform(1, 500)
        bbox_str = ",".join(map(str, compute_request_bbox(height, width, compute_request_center(CH_BBOX_WEBMERCATOR), resolution)))
        url = url_fmt.format(base=base_url, crs=crs, format_options=format_options, width=width, height=height, bbox=bbox_str, layernames=layer)
        urls.append(url)
    return urls

def parse_arguments(args):
    parser = ap.ArgumentParser(description="Generate WMS URLs")
    parser.add_argument("--base_url", type=str, default="/geoserver/wms", help="Base URL of the WMS service")
    parser.add_argument("--width", type=int, default=1000, help="Width of the image")
    parser.add_argument("--height", type=int, default=800, help="Height of the image")
    parser.add_argument("--nb_urls", type=int, default=10, help="Number of URLs to generate")
    parser.add_argument("--layer", type=str, default="layername", help="Layer name")
    parser.add_argument("--crs", type=str, default="EPSG:3857", help="CRS of the request")
    parser.add_argument("--format_options", type=str, default="dpi:135", help="Format options")
    return parser.parse_args(args)
    
if __name__ == "__main__":
    cli_args = parse_arguments(sys.argv[1:])
    base_url = cli_args.base_url
    width = cli_args.width
    height = cli_args.height
    nb_urls = cli_args.nb_urls
    layer = cli_args.layer
    crs = cli_args.crs
    format_options = cli_args.format_options
    
    urls = generate_wms_urls(CH_BBOX_WEBMERCATOR, base_url, width, height, nb_urls, layer, crs, format_options)
    
    for url in urls:
        print(url)
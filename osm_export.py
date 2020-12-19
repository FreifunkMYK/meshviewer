#!/usr/bin/env python3

import json
import requests
import xml.etree.ElementTree as ET
import sys
from math import sqrt

req = requests.get("https://www.openstreetmap.org/api/0.6/relation/" + sys.argv[1] + "/full")

if req.status_code != 200:
    sys.exit(1)

ways = {}
nodes = {}

paths = []

osm_xml = ET.fromstring(req.content)
nodes_xml = osm_xml.findall("node")
for node in nodes_xml:
    node_id = node.attrib["id"]
    node_lon = node.attrib["lon"]
    node_lat = node.attrib["lat"]
    nodes[node_id] = {"lon": node_lon, "lat": node_lat}
ways_xml = osm_xml.findall("way")
for way in ways_xml:
    way_id = way.attrib["id"]
    refs = []
    for nd in way:
        if not nd.tag == "nd":
            continue
        refs.append(nd.attrib["ref"])
    ways[way_id] = refs
relation = osm_xml.find('relation')
for member in relation:
    if not member.tag == "member":
        continue
    if not member.attrib["type"] == "way":
        continue
    way_id = member.attrib["ref"]
    path = []
    for nd in ways[way_id]:
        path.append([ float(nodes[nd]["lon"]), float(nodes[nd]["lat"]) ])
    paths.append(path)
ordered_path = []
for point in paths[0]:
    ordered_path.append(point)
del paths[0]
while len(paths):
    last_point = ordered_path[-1]
    first_point = paths[0][0]
    if last_point[0] == first_point[0] and last_point[1] == first_point[1]:
        for point in paths[0]:
            ordered_path.append(point)
    else:
        for point in reversed(paths[0]):
            ordered_path.append(point)
    del paths[0]
json.dump(ordered_path, open("path.json", "w"))

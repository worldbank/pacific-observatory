import os
from radiant_mlhub import Dataset

dataset = Dataset.fetch('ref_landcovernet_as_v1')

print(f'Title: {dataset.title}')
print(f'DOI: {dataset.doi}')
print(f'Citation: {dataset.citation}')
print('\nCollection IDs and License:')
for collection in dataset.collections:
    print(f'{collection.id} - {collection.license}')


asset_filter = dict(
    ref_landcovernet_af_v1_labels=['labels'],
)

import json
bb = """
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              139.04296875,
              -13.453737213419249
            ],
            [
              168.22265625,
              -13.453737213419249
            ],
            [
              168.22265625,
              -0.21972602392080884
            ],
            [
              139.04296875,
              -0.21972602392080884
            ],
            [
              139.04296875,
              -13.453737213419249
            ]
          ]
        ]
      }
    }
"""

my_geojson = json.loads(bb)

dataset.download(collection_filter=asset_filter, intersects=my_geojson)

dataset.download(collection_filter=asset_filter)


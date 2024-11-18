import ee

ee.Initialize()

wasatchFrontAreaBounding = ee.Geometry.Polygon([
  [-113, 40], [-113, 42],
  [-111, 42], [-111, 40]
])

images = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA').filterDate('2000-01-01', '2020-01-01').filterBounds(wasatchFrontAreaBounding).filterMetadata('CLOUD_COVER', 'less_than', 10)

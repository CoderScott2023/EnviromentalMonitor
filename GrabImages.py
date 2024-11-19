import ee
import cv2
import numpy

ee.Initialize()

wasatchFrontAreaBounding = ee.Geometry.Polygon([
  [-113, 40], [-113, 42],
  [-111, 42], [-111, 40]
])

images = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA').filterDate('2000-01-01', '2020-01-01').filterBounds(wasatchFrontAreaBounding).filterMetadata('CLOUD_COVER', 'less_than', 10)

def getMedianImageOfMonth(year, month):
  startDate = f'{year}-{month:02d}-01'
  endDate = f'{year}-{month:02d}-30' if month != 2 else f'{year}-{month:02d}-28'
  monthlyImages = images.filterDate(startDate, endDate).median()
  return monthlyImages

def createNDVImap(year, month):
  monthlyImages = getMedianImageOfMonth(year, month)
  ndvi = monthlyImages.normalizedDifference(["B4", "B5"])
  return ndvi

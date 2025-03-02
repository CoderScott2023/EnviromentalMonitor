import ee

ee.Authenticate()
ee.Initialize(project="project-id") #PUT YOUR GOOGLE CLOUD PROJECT ID HERE


landsat_5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA')
landsat_7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA')
landsat_8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')


geoCoordinates = ee.Geometry.Polygon([ #PLACE THE COORDINATES YOU WANT HERE
  [-113, 40], [-113, 42],
  [-111, 42], [-111, 40]
])

images = landsat_8 \
    .filterDate('2000-01-01', '2020-01-01') \
    .filterBounds(geoCoordinates)

def getMedianImageOfMonth(year, month):
    startDate = f'{year}-{month:02d}-01'
    endDate = f'{year}-{month:02d}-30' if month != 2 else f'{year}-{month:02d}-28'
    monthlyImages = images.filterDate(startDate, endDate).mean()
    return monthlyImages

def createNDVImap(year, month):
    monthlyImages = getMedianImageOfMonth(year, month)
    ndvi = monthlyImages.normalizedDifference(["B5", "B4"])
    return ndvi

for year in range(2000, 2021):
  if year == 2013 or year == 2014 or year == 2015:
    continue
    for month in range(1, 13):
        if year == 2016 and month != 12:
          continue
        ndviMap = createNDVImap(year, month)
        
        task = ee.batch.Export.image.toDrive(
            image=ndviMap.clip(geoCoordinates),
            description=f'NDVI_Year_{year}_Month_{month:02d}',
            folder='EarthEngineExports',
            scale=30,
            region=geoCoordinates.getInfo(),
            maxPixels=1e9
        )
      
        task.start()

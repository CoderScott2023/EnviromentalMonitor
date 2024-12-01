import ee

ee.Authenticate()
ee.Initialize(project="project-id") #not going to put my actual project id here for obvious reasons, especially cuz i wanna make this public sometime. Just know that it goes here for stuff like colab

wasatchFrontAreaBounding = ee.Geometry.Polygon([
  [-113, 40], [-113, 42],
  [-111, 42], [-111, 40]
])

images = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') \
    .filterDate('2000-01-01', '2020-01-01') \
    .filterBounds(wasatchFrontAreaBounding)

def getMedianImageOfMonth(year, month):
    startDate = f'{year}-{month:02d}-01'
    endDate = f'{year}-{month:02d}-30' if month != 2 else f'{year}-{month:02d}-28'
    monthlyImages = images.filterDate(startDate, endDate).median()
    return monthlyImages

def createNDVImap(year, month):
    monthlyImages = getMedianImageOfMonth(year, month)
    ndvi = monthlyImages.normalizedDifference(["B5", "B4"])
    return ndvi

for year in range(2000, 2021):
    for month in range(1, 13)
        ndviMap = createNDVImap(year, month)
        
        task = ee.batch.Export.image.toDrive(
            image=ndviMap.clip(wasatchFrontAreaBounding),
            description=f'NDVI_Year_{year}_Month_{month:02d}',
            folder='EarthEngineExports',
            scale=30,
            region=wasatchFrontAreaBounding.getInfo(),
            maxPixels=1e9
        )
      
        task.start()

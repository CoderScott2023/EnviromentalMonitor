import ee

ee.Authenticate()
ee.Initialize(project="boxwood-dynamo-419312")

wasatchFrontAreaBounding = ee.Geometry.Polygon([
    [-113, 40], [-113, 42],
    [-111, 42], [-111, 40]
])

landsat_5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA')
landsat_7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA')
landsat_8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')

images = landsat_5.merge(landsat_7).merge(landsat_8) \
    .filterDate('2000-01-01', '2020-01-01') \
    .filterBounds(wasatchFrontAreaBounding)

def maskClouds(image):
    qa = image.select('QA_PIXEL')
    cloudShadowBitMask = (1 << 3)
    cloudsBitMask = (1 << 5)
    mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
           qa.bitwiseAnd(cloudsBitMask).eq(0))
    return image.updateMask(mask)

images = images.map(maskClouds)

def getMedianImageOfMonth(year, month):
    startDate = ee.Date(f'{year}-{month:02d}-01')
    endDate = startDate.advance(1, 'month')
    monthlyImages = images.filterDate(startDate, endDate)
    if monthlyImages.size().getInfo() == 0:
        return None
    return monthlyImages.mean()

def createNDVImap(year, month):
    medianImage = getMedianImageOfMonth(year, month)
    if medianImage is None:
        return None
    return medianImage.normalizedDifference(["B5", "B4"]).rename("NDVI")

for year in range(2000, 2024):
    for month in range(1, 13):
        ndviMap = createNDVImap(year, month)
        if ndviMap is None:
            continue
        task = ee.batch.Export.image.toDrive(
            image=ndviMap.clip(wasatchFrontAreaBounding),
            description=f'NDVI_Year_{year}_Month_{month:02d}',
            folder='EarthEngineExports',
            scale=30,
            region=wasatchFrontAreaBounding,
            maxPixels=1e9
        )
        task.start()

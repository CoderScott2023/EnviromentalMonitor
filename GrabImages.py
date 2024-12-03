import ee

ee.Authenticate()
ee.Initialize(project="project-id") #not going to put my actual project id here for obvious reasons, especially cuz i wanna make this public sometime. Just know that it goes here for stuff like colab

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
    imageCount = monthlyImages.size().getInfo()

    if imageCount == 0:
        print(f"No images found for Year {year}, Month {month:02d}. Skipping...")
        return None
    print(f"Found {imageCount} images for Year {year}, Month {month:02d}.")
    return monthlyImages.mean()

def createNDVImap(year, month):
    monthlyImage = getMedianImageOfMonth(year, month)
    if monthlyImage is None:
        return None
    ndvi = monthlyImage.normalizedDifference(['B5', 'B4']).rename('NDVI')
    return ndvi

def exportNDVI(ndvi, year, month):
    task = ee.batch.Export.image.toDrive(
        image=ndvi,
        description=f'NDVI_{year}_{month:02d}',
        folder='NDVI_Maps',
        fileNamePrefix=f'NDVI_{year}_{month:02d}',
        region=wasatchFrontAreaBounding,
        scale=1000,
        maxPixels=1e9
    )
    task.start()
    print(f"Exporting NDVI map for Year {year}, Month {month:02d}...")

for year in range(2000, 2021):
    for month in range(1, 13):
        ndviMap = createNDVImap(year, month)
        if ndviMap:
            exportNDVI(ndviMap, year, month)

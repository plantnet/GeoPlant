"""Static manifest for the GeoPlant dataset downloader."""

VARIABLES = [
    "biogeographicalregions",
    "climate",
    "elevation",
    "humanfootprint",
    "landcover",
    "soilgrids",
    "satellitedata",
    "landsat",
]

PO_SENTINEL2_TIFF_PARTS = [
    f"SatelliteData/Sentinel2Patches-tiff/PO-Train-Sentinel2Patches-part-{part:02d}.zip"
    for part in range(24)
]

RASTERS = {
    "biogeographicalregions": [
        "EnvironmentalRasters/BiogeographicalRegions/Bioregions-Europe-2016-v1.geojson",
    ],
    "climate": [
        "EnvironmentalRasters/Climate/BioClimatic_Average_1981-2010.zip",
        "EnvironmentalRasters/Climate/Climatic_Monthly_1979-2019.zip",
    ],
    "elevation": [
        "EnvironmentalRasters/Elevation/ASTER_Elevation.tif",
    ],
    "humanfootprint": [
        "EnvironmentalRasters/HumanFootprint/v2/OSM_detailed.zip",
    ],
    "landcover": [
        "EnvironmentalRasters/LandCover/LandCover_MODIS_Terra-Aqua_500m.tif",
    ],
    "soilgrids": [
        "EnvironmentalRasters/Soilgrids/soilgrids.zip",
    ],
}

LEGACY_RASTERS = {
    "humanfootprint": [
        "EnvironmentalRasters/HumanFootprint/v1/summarized.zip",
        "EnvironmentalRasters/HumanFootprint/v1/detailed.zip",
    ],
}

PRESENCE_ONLY = {
    "climate": {
        "csvs": [
            "EnvironmentalValues/Climate/PO-train-bioclimatic.csv",
        ],
        "legacy_csvs": ["EnvironmentalValues/Climate/legacy/PO-train-bioclimatic-average.csv"],
    },
    "bioclim": {
        "csvs": ["TimeSeries/Bioclim/values/PO-train-bioclimatic_time_series.zip"],
        "cubes": [
            "TimeSeries/Bioclim/cubes/PO-train-bioclimatic-monthly.zip",
        ],
    },
    "elevation": {
        "csvs": ["EnvironmentalValues/Elevation/PO-train-elevation.csv"],
    },
    "humanfootprint": {
        "csvs": ["EnvironmentalValues/HumanFootprint/v2/PO-train-human_footprint.csv"],
        "legacy_csvs": ["EnvironmentalValues/HumanFootprint/v1/PO-train-human-footprint.csv"],
    },
    "landcover": {
        "csvs": ["EnvironmentalValues/LandCover/PO-train-landcover.csv"],
    },
    "soilgrids": {
        "csvs": ["EnvironmentalValues/SoilGrids/v2/PO-train-soilgrids.csv"],
        "legacy_csvs": ["EnvironmentalValues/SoilGrids/v1/PO-train-soilgrids.csv"],
    },
    "satellitedata": {
        "csvs": [
            "SatelliteData/Sentinel2Patches-jpeg/PO-Train-Sentinel2Patches-NIR.zip",
            "SatelliteData/Sentinel2Patches-jpeg/PO-Train-Sentinel2Patches-RGB.zip",
            PO_SENTINEL2_TIFF_PARTS,
            "SatelliteData/AlphaEarth/PO-train-alphaearth.parquet",
        ],
    },
    "landsat": {
        "csvs": [
            "TimeSeries/Landsat/values/PO-train-landsat-time-series.zip",
        ],
        "cubes": [
            "TimeSeries/Landsat/cubes/PO-train-landsat-time-series.zip",
        ],
    },
}

PRESENCE_ABSENCE = {
    "climate": {
        "csvs": [
            "EnvironmentalValues/Climate/PA-train-bioclimatic.csv",
            "EnvironmentalValues/Climate/PA-test-iid-bioclimatic.csv",
            "EnvironmentalValues/Climate/PA-test-ood-bioclimatic.csv",
            "EnvironmentalValues/Climate/PA-test-glc25-bioclimatic.csv",
        ],
        "legacy_csvs": [
            "EnvironmentalValues/Climate/legacy/PA-train-bioclimatic-average.csv",
            "EnvironmentalValues/Climate/legacy/PA-test-bioclimatic-average.csv",
        ],
    },
    "bioclim": {
        "csvs": [
            "TimeSeries/Bioclim/values/PA-train-bioclimatic_time_series.zip",
            "TimeSeries/Bioclim/values/PA-test-iid-bioclimatic_time_series.zip",
            "TimeSeries/Bioclim/values/PA-test-ood-bioclimatic_time_series.zip",
            "TimeSeries/Bioclim/values/PA-test-glc25-bioclimatic_time_series.zip",
        ],
        "cubes": [
            "TimeSeries/Bioclim/cubes/PA-train-bioclimatic-monthly.zip",
            "TimeSeries/Bioclim/cubes/PA-test-iid-bioclimatic-monthly.zip",
            "TimeSeries/Bioclim/cubes/PA-test-ood-bioclimatic-monthly.zip",
            "TimeSeries/Bioclim/cubes/PA-test-glc25-bioclimatic-monthly.zip",
        ],
    },
    "elevation": {
        "csvs": [
            "EnvironmentalValues/Elevation/PA-train-elevation.csv",
            "EnvironmentalValues/Elevation/PA-test-iid-elevation.csv",
            "EnvironmentalValues/Elevation/PA-test-ood-elevation.csv",
            "EnvironmentalValues/Elevation/PA-test-glc25-elevation.csv",
        ],
    },
    "humanfootprint": {
        "csvs": [
            "EnvironmentalValues/HumanFootprint/v2/PA-train-human_footprint.csv",
            "EnvironmentalValues/HumanFootprint/v2/PA-test-human_footprint.csv",
            "EnvironmentalValues/HumanFootprint/v2/PA-test-ood-human_footprint.csv",
            "EnvironmentalValues/HumanFootprint/v2/PA-test-glc25-human_footprint.csv",
        ],
        "legacy_csvs": [
            "EnvironmentalValues/HumanFootprint/v1/PA-train-human-footprint.csv",
            "EnvironmentalValues/HumanFootprint/v1/PA-test-human-footprint.csv",
        ],
    },
    "landcover": {
        "csvs": [
            "EnvironmentalValues/LandCover/PA-train-landcover.csv",
            "EnvironmentalValues/LandCover/PA-test-iid-landcover.csv",
            "EnvironmentalValues/LandCover/PA-test-ood-landcover.csv",
            "EnvironmentalValues/LandCover/PA-test-glc25-landcover.csv",
        ],
    },
    "soilgrids": {
        "csvs": [
            "EnvironmentalValues/SoilGrids/v2/PA-train-soilgrids.csv",
            "EnvironmentalValues/SoilGrids/v2/PA-test-iid-soilgrids.csv",
            "EnvironmentalValues/SoilGrids/v2/PA-test-ood-soilgrids.csv",
            "EnvironmentalValues/SoilGrids/v2/PA-test-glc25-soilgrids.csv",
        ],
        "legacy_csvs": [
            "EnvironmentalValues/SoilGrids/v1/PA-train-soilgrids.csv",
            "EnvironmentalValues/SoilGrids/v1/PA-test-soilgrids.csv",
        ],
    },
    "satellitedata": {
        "csvs": [
            "SatelliteData/Sentinel2Patches-jpeg/PA-Train-Sentinel2Patches-RGB+NIR.zip",
            "SatelliteData/Sentinel2Patches-jpeg/PA-Test-IID-Sentinel2Patches.zip",
            "SatelliteData/Sentinel2Patches-tiff/PA-Train-Sentinel2Patches.zip",
            "SatelliteData/Sentinel2Patches-tiff/PA-Test-IID-Sentinel2Patches.zip",
            "SatelliteData/Sentinel2Patches-tiff/PA-Test-OOD-Sentinel2Patches.zip",
            "SatelliteData/Sentinel2Patches-tiff/PA-Test-GLC25-Sentinel2Patches.zip",
            "SatelliteData/AlphaEarth/PA-train-alphaearth.parquet",
            "SatelliteData/AlphaEarth/PA-test-iid-alphaearth.parquet",
            "SatelliteData/AlphaEarth/PA-test-ood-alphaearth.parquet",
            "SatelliteData/AlphaEarth/PA-test-glc25-alphaearth.parquet",
        ],
    },
    "landsat": {
        "csvs": [
            "TimeSeries/Landsat/values/PA-train-landsat_time_series.zip",
            "TimeSeries/Landsat/values/PA-test-iid-landsat_time_series.zip",
            "TimeSeries/Landsat/values/PA-test-ood-landsat_time_series.zip",
            "TimeSeries/Landsat/values/PA-test-glc25-landsat_time_series.zip",
        ],
        "cubes": [
            "TimeSeries/Landsat/cubes/PA-train-landsat-time-series.zip",
            "TimeSeries/Landsat/cubes/PA-test-iid-landsat-time-series.zip",
            "TimeSeries/Landsat/cubes/PA-test-ood-landsat-time-series.zip",
            "TimeSeries/Landsat/cubes/PA-test-glc25-landsat-time-series.zip",
        ],
    },
}

METADATA = {
    "po": [
        "PresenceOnlyOccurrences/PO_metadata_train.csv",
    ],
    "pa": [
        "PresenceAbsenceSurveys/PA_metadata_train.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_iid.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_ood.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_glc25.csv",
    ],
}

REPOSITORY = "https://lab.plantnet.org/seafile/d/59325675470447b38add"
URL_STRUCT = f"{REPOSITORY}/files/?p=/{{}}"

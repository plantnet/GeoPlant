"""Static manifest for the GeoPlant dataset downloader."""

VARIABLES = [
    "biogeographicalregions",
    "climate",
    "elevation",
    "humanfootprint",
    "landcover",
    "soilgrids",
    "satellitepatches",
    "satellitetimeseries",
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
        "cubes": [
            "EnvironmentalValues/Climate/PO-train-bioclimatic.csv",
            "BioclimTimeSeries/cubes/PO-train-bioclimatic-monthly.zip",
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
    "satellitepatches": {
        "csvs": [
            "SatellitePatches/PO-Train-SatellitePatches-NIR.zip",
            "SatellitePatches/PO-Train-SatellitePatches-RGB.zip",
        ],
    },
    "satellitetimeseries": {
        "csvs": [
            "SatelliteTimeSeries/PO-train-landsat-time-series-swir2.csv",
            "SatelliteTimeSeries/PO-train-landsat-time-series-swir1.csv",
            "SatelliteTimeSeries/PO-train-landsat-time-series-red.csv",
            "SatelliteTimeSeries/PO-train-landsat-time-series-nir.csv",
            "SatelliteTimeSeries/PO-train-landsat-time-series-green.csv",
            "SatelliteTimeSeries/PO-train-landsat-time-series-blue.csv",
        ],
        "cubes": [
            "SatelliteTimeSeries/cubes/PO-train-landsat-time-series.zip",
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
        "cubes": [
            "EnvironmentalValues/Climate/PA-train-bioclimatic.csv",
            "EnvironmentalValues/Climate/PA-test-iid-bioclimatic.csv",
            "EnvironmentalValues/Climate/PA-test-ood-bioclimatic.csv",
            "EnvironmentalValues/Climate/PA-test-glc25-bioclimatic.csv",
            "BioclimTimeSeries/cubes/PA-train-bioclimatic-monthly.zip",
            "BioclimTimeSeries/cubes/PA-test-bioclimatic-monthly.zip",
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
    "satellitepatches": {
        "csvs": [
            "SatellitePatches/PA-Train-SatellitePatches-NIR.zip",
            "SatellitePatches/PA-Train-SatellitePatches-RGB.zip",
            "SatellitePatches/PA-Test-SatellitePatches-NIR.zip",
            "SatellitePatches/PA-Test-SatellitePatches-RGB.zip",
        ],
    },
    "satellitetimeseries": {
        "csvs": [
            "SatelliteTimeSeries/PA-train-landsat-time-series-swir2.csv",
            "SatelliteTimeSeries/PA-train-landsat-time-series-swir1.csv",
            "SatelliteTimeSeries/PA-train-landsat-time-series-red.csv",
            "SatelliteTimeSeries/PA-train-landsat-time-series-nir.csv",
            "SatelliteTimeSeries/PA-train-landsat-time-series-green.csv",
            "SatelliteTimeSeries/PA-train-landsat-time-series-blue.csv",
            "SatelliteTimeSeries/PA-test-landsat-time-series-swir2.csv",
            "SatelliteTimeSeries/PA-test-landsat-time-series-swir1.csv",
            "SatelliteTimeSeries/PA-test-landsat-time-series-red.csv",
            "SatelliteTimeSeries/PA-test-landsat-time-series-nir.csv",
            "SatelliteTimeSeries/PA-test-landsat-time-series-green.csv",
            "SatelliteTimeSeries/PA-test-landsat-time-series-blue.csv",
        ],
        "cubes": [
            "SatelliteTimeSeries/cubes/PA-train-landsat-time-series.zip",
            "SatelliteTimeSeries/cubes/PA-test-landsat-time-series.zip",
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
        "PresenceAbsenceSurveys/test_labels_iid.csv",
        "PresenceAbsenceSurveys/test_labels_ood.csv",
        "PresenceAbsenceSurveys/test_labels_glc25.csv",
    ],
}

REPOSITORY = "https://lab.plantnet.org/seafile/d/59325675470447b38add"
URL_STRUCT = f"{REPOSITORY}/files/?p=/{{}}"

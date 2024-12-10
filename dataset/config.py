variables = [
    'climate',
    'elevation',
    'humanfootprint',
    'landcover',
    'soilgrids',
    'satellitepatches',
    'satellitetimeseries'
]

rasters = {
    'climate': 'EnvironmentalRasters/Climate.zip',
    'elevation': 'EnvironmentalRasters/Elevation.zip',
    'humanfootprint': 'EnvironmentalRasters/HumanFootprint.zip',
    'landcover': 'EnvironmentalRasters/LandCover.zip',
    'soilgrids': 'EnvironmentalRasters/Soilgrids.zip'
}

presence_only = {
    'climate': {
        'csvs': [
            'EnvironmentalRasters/Climate/PO-train-bioclimatic-average.csv',
            'EnvironmentalRasters/Climate/PO-train-bioclimatic-monthly.csv'],
        'cubes': [
            'EnvironmentalRasters/Climate/PO-train-bioclimatic-average.csv',
            'EnvironmentalRasters/Climate/Climatic_Monthly_2000-2019_cubes/PO-train-bioclimatic-monthly.zip'
        ]
    },
    'elevation': {
        'csvs': ['EnvironmentalRasters/Elevation/PO-train-elevation.csv']
    },
    'humanfootprint': {
        'csvs': ['EnvironmentalRasters/HumanFootprint/PO-train-human-footprint.csv']
    },
    'landcover': {
        'csvs': ['EnvironmentalRasters/LandCover/PO-train-landcover.csv']},
    'soilgrids': {
        'csvs': ['EnvironmentalRasters/Soilgrids/PO-train-soilgrids.csv']
    },
    'satellitepatches': {
        'csvs': [
            'SatellitePatches/PO-Train-SatellitePatches-NIR.zip',
            'SatellitePatches/PO-Train-SatellitePatches-RGB.zip'
        ]
    },
    'satellitetimeseries': {
        'csvs': [
            'SatelliteTimeSeries/PO-train-landsat-time-series-swir2.csv',
            'SatelliteTimeSeries/PO-train-landsat-time-series-swir1.csv',
            'SatelliteTimeSeries/PO-train-landsat-time-series-red.csv',
            'SatelliteTimeSeries/PO-train-landsat-time-series-nir.csv',
            'SatelliteTimeSeries/PO-train-landsat-time-series-green.csv',
            'SatelliteTimeSeries/PO-train-landsat-time-series-blue.csv',
        ],
        'cubes': [
            'SatelliteTimeSeries/cubes/PO-train-landsat-time-series.zip'
        ]
    }
}

presence_absence = {
    'climate': {
        'csvs': [
            'BioclimTimeSeries/values/PA-test-bioclimatic-average.csv',
            'BioclimTimeSeries/values/PA-test-bioclimatic-monthly.csv',
            'BioclimTimeSeries/values/PA-train-bioclimatic-average.csv',
            'BioclimTimeSeries/values/PA-train-bioclimatic-monthly.csv',
            'BioclimTimeSeries/cubes/PO-train-bioclimatic-average.csv',
            'BioclimTimeSeries/cubes/PO-train-bioclimatic-monthly.csv'],
        'cubes': [
            'BioclimTimeSeries/cubes/PA-test-bioclimatic-monthly.zip',
            'BioclimTimeSeries/cubes/PA-train-bioclimatic-monthly.zip',
        ]
    },
    'elevation': {
        'csvs': [
            'EnvironmentalRasters/Elevation/PA-train-elevation.csv',
            'EnvironmentalRasters/Elevation/PA-test-elevation.csv']
    },
    'humanfootprint': {
        'csvs': [
            'EnvironmentalRasters/HumanFootprint/PA-train-human-footprint.csv',
            'EnvironmentalRasters/HumanFootprint/PA-test-human-footprint.csv'
        ]
    },
    'landcover': {
        'csvs': [
            'EnvironmentalRasters/LandCover/PA-train-landcover.csv',
            'EnvironmentalRasters/LandCover/PA-test-landcover.csv'
        ]
    },
    'soilgrids': {
        'csvs': [
            'EnvironmentalRasters/Soilgrids/PA-train-soilgrids.csv',
            'EnvironmentalRasters/Soilgrids/PA-test-soilgrids.csv'
        ]
    },
    'satellitepatches': {
        'not_cubes': [
            'SatellitePatches/PA-Train-SatellitePatches-NIR.zip',
            'SatellitePatches/PA-Train-SatellitePatches-RGB.zip',
            'SatellitePatches/PA-Test-SatellitePatches-NIR.zip',
            'SatellitePatches/PA-Test-SatellitePatches-RGB.zip'
        ]
    },
    'satellitetimeseries': {
        'csvs': [
            'SatelliteTimeSeries/PA-train-landsat-time-series-swir2.csv',
            'SatelliteTimeSeries/PA-train-landsat-time-series-swir1.csv',
            'SatelliteTimeSeries/PA-train-landsat-time-series-red.csv',
            'SatelliteTimeSeries/PA-train-landsat-time-series-nir.csv',
            'SatelliteTimeSeries/PA-train-landsat-time-series-green.csv',
            'SatelliteTimeSeries/PA-train-landsat-time-series-blue.csv',
            'SatelliteTimeSeries/PA-test-landsat-time-series-swir2.csv',
            'SatelliteTimeSeries/PA-test-landsat-time-series-swir1.csv',
            'SatelliteTimeSeries/PA-test-landsat-time-series-red.csv',
            'SatelliteTimeSeries/PA-test-landsat-time-series-nir.csv',
            'SatelliteTimeSeries/PA-test-landsat-time-series-green.csv',
            'SatelliteTimeSeries/PA-test-landsat-time-series-blue.csv'
        ],
        'cubes': [
            'SatelliteTimeSeries/cubes/PA-train-landsat-time-series.zip',
            'SatelliteTimeSeries/cubes/PA-test-landsat-time-series.zip'
        ]
    }
}

metadata = {
    'po': [
        'PresenceOnlyOccurrences/PO_metadata_train.csv'
    ],
    'pa': [
        'PresenceAbsenceSurveys/PA_metadata_test.csv',
        'PresenceAbsenceSurveys/PA_metadata_train.csv'
    ]
}
repository = 'https://lab.plantnet.org/seafile/d/59325675470447b38add'
url_struct = f'{repository}/files/?p=/{{}}'

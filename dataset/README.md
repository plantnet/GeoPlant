# GeoPlant Dataset Downloader

## Download instructions

There are two options to download the dataset:
1. Download the whole dataset from kaggle [~45GB]
2. Use the download script (preferred)

### 1. Download the dataset from kaggle [~45GB]:
While the structure of the data is kept the same, using the Kaggle API, you have to always download all the data.

To download the data, you have to:
1. Register and login to Kaggle.
2. Install Kaggle API `pip install kaggle`
4. Store Kaggle login settings and locally.
   ```
   !mkdir ~/.kaggle
   !touch ~/.kaggle/kaggle.json
   api_token = {"username":"FILL YOUR USERNAME","key":"FILL YOUR APIKEY"}
   ```
5. Use CLI `kaggle datasets download -d picekl/geoplant`

### 2. Use the download script
The preferred approach is to use our script to get the data that allows downloading different modalities/predictors separately.

The following example downloads ...... and saves it in the current directory.
You can select where to store the data with the option ```--data path_to_data```.



```
cd datasets
python download.py --metadata --images --subset "m" --size "300" --save_path "./"  
```

The script requires that you **first** select either PA or PO data.

[info] If you do not select it, both will be downloaded.

```
Data sources:
  --presence-only       Download PO metadata and pre-extracted data if selected
  --presence-absence    Download PA metadata and pre-extracted data if selected
```

then select the data type you want to download,

```
Data type:
  --metadata            Download observation metadata
  --rasters             Download full Europe scale rasters
  --csvs                Download pre-extracted data of PO and/or PA depending on the options set
  --cubes               Download cube data instead of csv. when available
```

and then select the variables you want to download :
```
Variables:
  --climate             Download climate raster or pre-extracted data
  --elevation           Download elevation raster or pre-extracted data
  --humanfootprint      Download humanfootprint raster or pre-extracted data
  --landcover           Download landcover raster or pre-extracted data
  --soilgrids           Download soilgrids raster or pre-extracted data
  --satellitepatches    Download satellitepatches raster or pre-extracted data
  --satellitetimeseries
                        Download satellitesimeseries raster or pre-extracted data
  --all-variables       Select all variables
  ```
  
You can also select all variables using the ```--all-variables``` option. 
  
All combination of paramters do not necessarily lead to existing data (e.g. there is not ```raster``` for ```satellitepatches```). The script will download what's available.

Downloading segmentation masks, climate data and satellite images:

```
cd datasets
python download.py --masks --climatic --satellite --save_path "./"  
```
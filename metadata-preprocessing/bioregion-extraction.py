import geopandas as gpd
from tqdm import tqdm
import pandas as pd
import time
from joblib import Parallel, delayed
import os

# Define global variables to be used by the parallel function
global_polygons = None
global_polygons_sindex = None


def read_polygons(file_path):
    """
    Read and preprocess polygons from a GeoJSON file.

    Args:
        file_path (str): Path to the GeoJSON file.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing the polygons with CRS set to EPSG:4326.
    """
    try:
        polygons = gpd.read_file(file_path)
        polygons = polygons.to_crs("EPSG:4326")
        return polygons
    except Exception as e:
        raise RuntimeError(f"Error reading polygons file: {e}")


def read_gps_data(file_path, longitude_col="lon", latitude_col="lat"):
    """
    Read and preprocess GPS data from a CSV file.

    Args:
        file_path (str): Path to the CSV file.
        longitude_col (str): Name of the column containing the longitude.
        latitude_col (str): Name of the column containing the latitude.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing the GPS data with points geometry.
    """
    try:
        gps_data = pd.read_csv(file_path, dtype={"speciesId": int})
        gps_data = gps_data.drop_duplicates("surveyId").reset_index(drop=True)
        gps_gdf = gpd.GeoDataFrame(gps_data,
                                   geometry=gpd.points_from_xy(gps_data[longitude_col],
                                                               gps_data[latitude_col]),
                                   crs="EPSG:4326")
        return gps_gdf
    except Exception as e:
        raise RuntimeError(f"Error reading GPS data file: {e}")


def find_polygon_id(point):
    """
    Find the polygon ID that contains the given point.

    Args:
        point (shapely.geometry.Point): The point to check.

    Returns:
        str: The short name of the polygon that contains the point, or None if no polygon contains the point.
    """
    possible_matches_index = list(global_polygons_sindex.query(point))
    possible_matches = global_polygons.iloc[possible_matches_index]
    for _, row in possible_matches.iterrows():
        if row['geometry'].contains(point):
            return row['short_name']
    return None


def process_point(point):
    """
    Wrapper function for parallel processing to call find_polygon_id.

    Args:
        point (shapely.geometry.Point): The point to process.

    Returns:
        str: The polygon ID.
    """
    return find_polygon_id(point)


def assign_polygon_ids(gps_gdf, polygons, n_jobs=-1):
    """
    Assign polygon IDs to GPS data points using parallel processing.

    Args:
        gps_gdf (gpd.GeoDataFrame): GeoDataFrame containing GPS data points.
        polygons (gpd.GeoDataFrame): GeoDataFrame containing polygons.
        n_jobs (int): The number of jobs to run in parallel. -1 means using all processors.

    Returns:
        pd.Series: Series containing the polygon IDs for each GPS data point.
    """
    global global_polygons, global_polygons_sindex
    global_polygons = polygons
    global_polygons_sindex = polygons.sindex

    polygon_ids = Parallel(n_jobs=n_jobs)(
        delayed(process_point)(point) for point in tqdm(gps_gdf.geometry,
                                                        desc="Assigning polygon IDs")
    )
    return pd.Series(polygon_ids)


def save_gps_data(gps_gdf, output_path):
    """
    Save the updated GPS data to a CSV file.

    Args:
        gps_gdf (gpd.GeoDataFrame): GeoDataFrame containing GPS data with polygon IDs.
        output_path (str): Path to the output CSV file.
    """
    try:
        gps_gdf.drop(columns='geometry').to_csv(output_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Error saving GPS data to file: {e}")


def main(polygons_file_path, gps_data_file_path, output_file_path, n_jobs=-1):
    """
    Main function to read, process, and save GPS data with assigned polygon IDs.

    Args:
        polygons_file_path (str): Path to the GeoJSON file with polygons.
        gps_data_file_path (str): Path to the CSV file with GPS data.
        output_file_path (str): Path to the output CSV file.
        n_jobs (int): The number of jobs to run in parallel. -1 means using all processors.
    """
    print("Extraction started.")
    start_time = time.time()

    # Read and process data
    polygons = read_polygons(polygons_file_path)
    gps_gdf = read_gps_data(gps_data_file_path)

    # Assign polygon IDs
    gps_gdf['polygon_id'] = assign_polygon_ids(gps_gdf, polygons, n_jobs=n_jobs)

    # Save results
    save_gps_data(gps_gdf, output_file_path)

    print(f"Elapsed time: {time.time() - start_time:.2f} seconds")
    print("Done!")


if __name__ == "__main__":
    # First download the BioRegion definition!
    # https://sdi.eea.europa.eu/catalogue/idp/api/records/c6d27566-e699-4d58-a132-bbe3fe01491b

    polygons_file_path = '../resources/Bioregions-Europe-2016-v1.geojson'
    gps_data_file_path = '../metadata/GLC24-PA-metadata-test.csv'
    output_file_path = 'gps_data_with_polygon_ids.csv'

    main(polygons_file_path, gps_data_file_path, output_file_path)

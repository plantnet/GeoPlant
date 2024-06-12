import pandas as pd
from joblib import Parallel, delayed
import reverse_geocoder as rg
import multiprocessing
from tqdm import tqdm
import os
import time

# Number of parallel jobs
n_jobs = multiprocessing.cpu_count()


def upscale_gps(lat, lon, survey_id):
    """
    Perform reverse geocoding to get location data for a GPS coordinate.

    Args:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        survey_id (int): ID of the survey.

    Returns:
        dict: Dictionary with location data and survey ID.
    """
    try:
        location = rg.search((lat, lon), mode=1)[0]
        location_data = {
            'county': location['admin1'],
            'district': location['admin2'],
            'surveyId': survey_id
        }
        return location_data
    except Exception as e:
        print(f"Error processing point ({lat}, {lon}): {e}")
        return None


def process_gps_data(file_path):
    """
    Process GPS data from a CSV file by adding location details using reverse geocoding.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing GPS data with added location details.
    """
    try:
        gps_data = pd.read_csv(file_path, dtype={'speciesId': int})
        unique_surveys = gps_data.drop_duplicates("surveyId").reset_index(drop=True)

        # Extract latitude, longitude, and survey ID for processing
        surveys = unique_surveys[["lat", "lon", "surveyId"]]

        location_data = Parallel(n_jobs=n_jobs)(
            delayed(upscale_gps)(row['lat'], row['lon'], row['surveyId'])
            for _, row in tqdm(surveys.iterrows(), total=len(surveys), desc="Geocoding GPS data")
        )

        # Remove None results and create DataFrame
        location_data = [loc for loc in location_data if loc is not None]
        location_df = pd.DataFrame(location_data)

        # Merge with original data
        updated_data = gps_data.merge(location_df, on='surveyId', how='left')
        return updated_data
    except Exception as e:
        raise RuntimeError(f"Error processing GPS data: {e}")


def save_updated_data(data, output_path):
    """
    Save updated GPS data to a CSV file.

    Args:
        data (pd.DataFrame): DataFrame containing the updated GPS data.
        output_path (str): Path to save the output CSV file.
    """
    try:
        data.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    except Exception as e:
        raise RuntimeError(f"Error saving data to file: {e}")


def main(input_file, output_file):
    """
    Main function to process GPS data from input file and save updated data to output file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
    """
    print("Processing started.")
    start_time = time.time()

    updated_data = process_gps_data(input_file)

    save_updated_data(updated_data, output_file)

    elapsed_time = time.time() - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    # File paths for input and output
    input_file_path = "../metadata/GLC24-PA-metadata-train.csv"
    output_file_path = "../metadata/PA_metadata_train.csv"

    main(input_file_path, output_file_path)

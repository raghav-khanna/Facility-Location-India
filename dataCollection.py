from bs4 import BeautifulSoup
from dotenv import dotenv_values
import requests
import psycopg2
from math import radians
import csv


def main():
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details.DB_NAME, user=db_details.DB_USER, password=db_details.DB_PASS, host=db_details.DB_HOST)
    cur = conn.cursor()
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS districts(id SERIAL PRIMARY KEY,name TEXT NOT NULL,state TEXT NOT NULL,pop_density INTEGER NOT NULL,latitude NUMERIC(7,6),longitude NUMERIC(7,6));")
        # cur.execute("TRUNCATE TABLE districts RESTART IDENTITY CASCADE;")
        # cur.execute("INSERT INTO districts(name, state, pop_density, latitude, longitude) VALUES (%s,%s);", (name, state, pop_density, latitude, longitude))
        conn.commit()
    except:
        print("failed to create table")
    finally:
        cur.close()
        conn.close()
        return


def get_districts(url):
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table')

        # Initialize an empty list to store the table data
        table_data = []

        for row in table.find_all('tr'):
            row_data = []
            # Iterate through the cells (columns) of each row
            cells = row.find_all(['th', 'td'])

            for cell in row.find_all(['th', 'td']):
                row_data.append(cell.get_text(strip=True))

            if cells[0].get_text(strip=True) != '#':
                # Calculate and add the 'Density' column
                # Remove commas and convert to float
                population = float(row_data[5].replace(',', ''))
                # Remove commas and convert to float
                area = float(row_data[4].replace(',', ''))
                density = population / area
                row_data.append(density)
            else:
                row_data.append('Density')
            altered_row_data = []

            for i in range(len(row_data)):
                if i == 1 or i == 3 or i == 7:
                    altered_row_data.append(row_data[i])

            table_data.append(altered_row_data)

        # Define the name for the CSV file where you want to save the table data
        csv_filename = 'data/districts_data.csv'

        # Write the table data to a CSV file
        with open(csv_filename, 'wb') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row_data in table_data:
                csv_writer.writerow(row_data)

        print('Table data has been extracted and saved as : ', csv_filename)
    else:
        print('Failed to retrieve the webpage. Status code:', response.status_code)


# Function to make a GET request to the PositionStack API
def get_location_info(district):
    # Replace with your PositionStack API key
    api_key = 'd0905eff7bc12206ec8e6db40662f5c4'
    base_url = 'http://api.positionstack.com/v1/forward'
    query_params = {
        'access_key': api_key,
        'country': 'IN',
        'query': district
    }
    response = requests.get(base_url, params=query_params)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]  # Return the first result
    return None


def getLatLong():
    # Read the existing CSV file
    csv_filename = 'Data/districts_data.csv'
    new_csv_filename = 'Data/coordinates_data.csv'
    with open(csv_filename, 'rb') as csv_file:  # Use 'rb' mode for reading binary data
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Read and store the header

        # Create a new CSV file and write the header
        with open(new_csv_filename, 'wb') as new_csv_file:
            csv_writer = csv.writer(new_csv_file)
            csv_writer.writerow(header + ['Latitude', 'Longitude'])

            # Iterate through the rows
            for row in csv_reader:
                # 'District' column is the second column (index 1)
                district = row[1]
                location_info = get_location_info(district)
                if location_info:
                    latitude = location_info.get('latitude', '')
                    longitude = location_info.get('longitude', '')
                    csv_writer.writerow(row + [latitude, longitude])
                else:
                    # Empty values if data not found
                    csv_writer.writerow(row + ['', ''])

    print('New CSV file with location information has been created:', new_csv_filename)


if __name__ == "__main__":
    main()

    # lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    districts_url = 'https://www.censusindia.co.in/districts'
    get_districts(districts_url)

    # Creates the combined data CSV file
    getLatLong()

import requests
from xml.etree import ElementTree as ET

def get_arxiv_papers(query: str, max_results: int = 5, sort_by: str = 'relevance', sort_order: str = 'descending'):
    try:
        # Define the base URL for the arXiv API query
        base_url = 'https://export.arxiv.org/api/query'

        # Set the payload for the query parameters
        payload = {
            'search_query': query,
            'sortBy': sort_by,
            'sortOrder': sort_order,
            'max_results': max_results
        }

        # Send a GET request to the arXiv API
        response = requests.get(base_url, params=payload)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()

        # Parse the XML response content from arXiv
        root = ET.fromstring(response.content)
        results = []

        # Extract paper information from each entry in the XML
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            # Extract essential elements from the entry
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            published = entry.find('{http://www.w3.org/2005/Atom}published').text.strip()
            link = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]').attrib['href']

            # Accumulate the paper information into a list
            results.append({
                'title': title,
                'summary': summary,
                'published': published,
                'link': link
            })

        return results
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None

import requests

def get_weather_forecast(latitude: float, longitude: float, current_weather: bool = True, hourly_forecast: bool = False, daily_forecast: bool = False):
    try:
        # Define the base URL for the Open-Meteo API
        base_url = 'https://api.open-meteo.com/v1/forecast'

        # Set up the parameters for the API request
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current_weather': current_weather,
            'hourly': hourly_forecast,
            'daily': daily_forecast
        }
        # Filter out unwanted params (those that are set to False)
        params = {k: v for k, v in params.items() if v is not False}

        # Send a GET request to the Open-Meteo API
        response = requests.get(base_url, params=params)

        # Raise an exception if the response was unsuccessful
        response.raise_for_status()

        # Return the JSON response if successful
        return response.json()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None

import requests

def fetch_json_data(url):
    """
    Fetches JSON data from a specified URL.

    Parameters:
        url (str): The URL from which to fetch the JSON data.

    Returns:
        dict: The JSON data parsed into a dictionary.
        None: If the request fails or the response is not JSON.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json()      # Returns the JSON content
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except ValueError:
        print("Invalid JSON")
        return None


def get_btc_price():
    try:
        data = fetch_json_data('https://mempool.space/api/v1/prices')
        return data.get('USD', 65_000)
    except:
        return 65_000

def get_avg_block_fee_24h():
    try:
        data = fetch_json_data('https://mempool.space/api/v1/mining/blocks/fees/24h')
        return sum([d['avgFees'] for d in data]) / len(data) / 1E8
    except:
        return 0.3

def get_block_difficulty():
    try:
        return fetch_json_data('https://mempool.space/api/v1/mining/difficulty-adjustments/1m')[0][2] / 1E12
    except:
        return 90.

def get_usd_rmb():
    try:
        return fetch_json_data('https://open.er-api.com/v6/latest/USD').get('rates').get('CNY')
    except:
        return 7.

def get_usd_kzt():
    try:
        return fetch_json_data('https://open.er-api.com/v6/latest/USD').get('rates').get('KZT')
    except:
        return 442.
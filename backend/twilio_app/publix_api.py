from backend.resources import SubDeal
from backend.resources import initialize_database
import requests
import html
from pprint import pprint
import re

def query_deals(store_id, sort_by_term="onsalemsg"):
    """
    Query the Publix API for deals on subs at the given store by its ID.

    :param store_id: String of the store id:
            Should be either five digits with a 0 (e.g. "09999")
            Or four digits without (e.g. "999")

    :param sort_by_term: String to sort the results by, default is "onsalemsg",
                         which sorts the subs on sale as first.

    :return: Dictionary of the deals
    """

    response = requests.request(
        "GET",
        "https://services.publix.com/api/v4/ispu/product/Search?",
        data="",
        headers={},
        params={
            "storeNumber": store_id,
            "rowCount": "200",
            "orderAheadOnly": "true",
            "categoryID": "d3a5f2da-3002-4c6d-949c-db5304577efb",
            "sort": sort_by_term,
        },
    )

    decoded_data = response.json()
    sale_dict = []

    for product in decoded_data['Products']:
        if product['onsalemsg'] == 'On Sale' and "Sub" in product['title']:
            pprint(product)
            name = re.sub("®", "", html.unescape(product['title']))
            price = re.sub("Starts At \\$", "", product['priceline1'])
            product_id = product['Productid']

            sale_dict.append({'name': name,
                              'price': price,
                              'product_id': product_id})

    if sale_dict:
        print(f"Found {len(sale_dict)} deals at store ID: {store_id}")
        pprint(sale_dict)
    else:
        print(f"No deals found at store ID: {store_id}")

    return sale_dict

def find_publix_store_id(zip_code, store_name):
    """Get the store ID for the given store name and zip code.



    :param zip_code: String, zip code of the store
    :param store_name: String, name of the store LOCATION "St. John's Town Center"
    :return:
    """
    response = requests.request(
        "GET",
        "https://services.publix.com/api/v1/storelocation",
        data="",
        headers={},
        params={
            "types": "R,G,H,N,S",
            "option": "",
            "count": "5",
            "includeOpenAndCloseDates": "true",
            "isWebsite": "true",
            "zipCode": zip_code,
        },
    )

    response = response.json()
    pprint(response)

    store_dict = []

    for store in response['Stores']:
        store_name = html.unescape(store['NAME'])
        store_address = store['ADDR']
        store_id = store['KEY']
        store_entry = {'name': store_name, 'address': store_address, 'store_id': store_id}
        store_dict.append(store_entry)

    for store in store_dict:
        if store['name'] == store_name:
            print(f"Found store ID: {store['store_id']}")
            return store['store_id']

def find_sub_id(store_id, sub_name):
    """Find the product ID for the given sub name and store ID.

    :param store_id: String, store ID
    :param sub_name: String, name of the sub
    :return: String, product ID
    """
    response = requests.request(
        "GET",
        "https://services.publix.com/api/v4/ispu/product/Search?",
        data="",
        headers={},
        params={
            "storeNumber": store_id,
            "rowCount": "200",
            "orderAheadOnly": "true",
            "categoryID": "d3a5f2da-3002-4c6d-949c-db5304577efb",
            "sort": "onsalemsg"
        },
    )

    response = response.json()
    found_product_id = None
    for product in response['Products']:
        cleaned_title = re.sub('®', '', html.unescape(product['title']))
        if cleaned_title == sub_name:
            found_product_id = product['Productid']
            break

    if found_product_id is None:
        raise ValueError(f"Could not find product ID for {sub_name} at store {store_id}")

    return found_product_id


if __name__ == '__main__':
    query_deals(store_id="00589")

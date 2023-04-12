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
        if product['onsalemsg'] == 'On Sale':
            name = html.unescape(product['title'])
            price = re.sub("Starts At ", "", product['priceline1'])
            product_id = product['Productid']

            sale_entry = {'name': name, 'price': price, 'product_id': product_id}
            sale_dict.append(sale_entry)

    pprint(sale_dict)
    return sale_dict

def find_publix_store_id(zip_code, store_name):
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
            return store['store_id']

if __name__ == '__main__':
    find_publix_store_id('33458')

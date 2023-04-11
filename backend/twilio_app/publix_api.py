from backend.resources import SubDeal
from backend.resources import initialize_database
import requests
import html
from pprint import pprint

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
    url = f"https://services.publix.com/api/v4/ispu/product/Search?" \
          f"storeNumber={store_id}&rowCount=200&orderAheadOnly=true&" \
          f"categoryID=d3a5f2da-3002-4c6d-949c-db5304577efb&sort={sort_by_term}"

    response = requests.get(url)

    decoded_data = response.json()

    sale_dict = []

    for product in decoded_data['Products']:
        if product['onsalemsg'] == 'On Sale':
            name = html.unescape(product['title'])
            price = product['priceline1']
            product_id = product['Productid']

            sale_entry = {'name': name, 'price': price, 'product_id': product_id}
            sale_dict.append(sale_entry)

    pprint(sale_dict)
    return sale_dict


if __name__ == '__main__':
    query_deals('1121')
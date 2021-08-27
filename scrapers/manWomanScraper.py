# from unicodedata import category

import requests
import time
import json
import csv
from datetime import datetime
from bs4 import BeautifulSoup

from shared.Product import Product
import shared.util as util



base_url = 'https://manwomanhome.com'
logger = util.get_logger()

file_name = 'results/results_' + datetime.now().strftime("%m-%d-%Y__%H-%M-%S") + ".csv"

csv_columns = ['Date Scraped', 'Website', 'Url', 'Gender', 'Category', 'Sub Category', 'Title', 'Brand',  'Price', 'Sale Price', 'Description', 'Stock Availability', 'Available Sizes & Colors', 'Reviews', 'Ratings', 'Images']


def start_scraping():
    time_Scraper_Started = '' # for time deltas.
    
    
    logger.debug('...')
    logger.debug('Statrting scraping process...')
    
    response_html = make_http_request(base_url)
    if response_html != '':
        
        #################################################
        # get the main 4 options from the navigation menu
        # MAN, WOMAN, ACCESSORIES, SALE
        #################################################
        soup = BeautifulSoup(response_html, "html.parser")
        main_categories = soup.select('ul[id="AccessibleNav"]>li[class="site-nav__item site-nav--has-dropdown"]')
        
        if not len(main_categories).__eq__(0):
            
            all_category_urls = []
                        
            logger.debug(str(len(main_categories)) + ' main navigational options found.')
            
            ###########################################################
            # get all the available URLs present in the navigation menu
            # for eg: 
            # -/l-s-button-up
            # -/s-s-t-shirts
            # -/l-s-t-shirts
            ###########################################################
            for index, category in enumerate(main_categories):
                new_urls = extract_all_category_urls(index, category)
                if len(new_urls) > 0:
                    all_category_urls.extend(new_urls)
            
            if len(all_category_urls) > 0:
                
                ###########################
                # write headers to csv file
                ###########################
                write_headers_to_csv()
                
                ###################################################################
                # now, visit every url and paginate through all available pages and 
                # get the URLs of all the available products in the category list
                ###################################################################
                for category in all_category_urls:  ### https://manwomanhome.com/collections/l-s-button-up
                    try:
                        #############################################################
                        # get all the products in the category and at the end of this
                        # loop write it in csv file.
                        #############################################################
                        products = []
                    
                        found_products_urls = get_product_urls(category)
                        
                        if len(found_products_urls) > 0:
                            found_products_count = str(len(found_products_urls))
                            logger.debug('#####################################################')
                            logger.debug('### '+ category['gender'] + ' - ' + category['category'] + ' - '+ category['sub_category'] + ' - (' + found_products_count + ')')
                            logger.debug('#####################################################')
                            
                            ########################################################
                            # visit every product page and extract the required info
                            ########################################################
                            for index, product_url_handle in enumerate(found_products_urls):
                                try:
                                    product_url = base_url + product_url_handle.attrs['href'] ### https://manwomanhome.com/collections/l-s-button-up/products/wilder-s-s-button-up
                                    
                                    ########################################################
                                    # check if the found product is already extracted or not
                                    ########################################################
                                    found = [pro for pro in products if pro.url.__eq__(product_url)]
                                    if found:
                                        logger.warning('Duplicate Detected => ' + product_url)
                                    else:
                                        found_product = extract_product_info(product_url, category)
                                        if found_product is not None:
                                            
                                            ########################################################
                                            # check if the found product is already extracted or not
                                            ########################################################
                                            found = [pro for pro in products if pro.title.__eq__(found_product.title) and pro.brand.__eq__(found_product.brand)]
                                            if found:
                                                logger.warning('Duplicate Detected => ' + found_product['title'])
                                            else:
                                                products.append(found_product)
                                                
                                                logger.debug('-----------------------------------------------------')
                                                logger.debug('[' + str(index) + '/' + found_products_count + '] =>>> ' + found_product.title + '  |  ' + str(found_product.price))
                                                logger.debug('-----------------------------------------------------')
                                                
                                except Exception as p_ex:
                                    logger.error('product_url(loop)=> ' + str(p_ex))

                        ##########################################
                        # write the extracted products to csv file
                        ##########################################
                        export_to_csv(products)
                    except Exception as c_ex:
                        logger.error('all_category_urls(loop)=> ' + str(c_ex))
        else:
            logger.warning('Unable to get navigation menu.')


def extract_all_category_urls(main_index, main_categoy):
    urls = []
    
    try:
        node = main_categoy.select_one('a')
        if node:
            gender = node.text.strip()
            
        li_items = main_categoy.select('ul[class="site-nav__dropdown site-nav--has-grandchildren"]>li')
        if not len(li_items).__eq__(0):
            logger.debug('- ' + str(main_index) + ' - [' + gender + '] (' + str(len(li_items)) + ')')
            
            for li_index, item in enumerate(li_items):
                try:
                    node = item.select_one('a')
                    if node:
                        category = node.text.strip()
                        
                    sub_li_items = item.select('div>ul>li>a')
                    if not len(sub_li_items).__eq__(0):
                        logger.debug('-- ' + str(li_index) + ' - [' + category + '] (' + str(len(sub_li_items)) + ')')
                        
                        for sub_index, sub in enumerate(sub_li_items):
                            try:
                                url = base_url + sub.attrs['href']
                                sub_cat = sub.text.strip()
                                # logger.debug('----- ' + str(sub_index) + ' - <' + sub_cat + '>')
                                urls.append({'gender' : gender, 'category': category, 'sub_category': sub_cat, 'url': url })
                            except Exception as excp:
                                logger.error('extract_all_category_urls()=> ' + str(excp))
                    else:
                        url = base_url + node.attrs['href']
                        # logger.debug('-- ' + str(li_index) + ' - [' + category + '] ()')
                        urls.append({'gender' : gender, 'category': category, 'sub_category': '', 'url': url })
                except Exception as exc:
                    logger.error('extract_all_category_urls()=> ' + str(exc))
        else:
            li_items = main_categoy.select('ul>li')
            if not len(li_items).__eq__(0):
                logger.debug('- ' + str(main_index) + ' - [' + gender + '] (' + str(len(li_items)) + ')')
                
                for li_index, item in enumerate(li_items):
                    try:
                        node = item.select_one('a')
                        if node:
                            category = node.text.strip()
                            url = base_url + node.attrs['href']
                            # logger.debug('-- ' + str(li_index) + ' - [' + category + '] ()')
                            urls.append({'gender' : category, 'category': gender, 'sub_category': '', 'url': url })
                    except Exception as excp:
                        logger.error('extract_all_category_urls()=> ' + str(excp))
    except Exception as ex:
        logger.error('extract_all_category_urls()=> ' + str(ex))
        
    return urls

    
def make_http_request(url):
    retry = 0
    responseTxt = ''

    while retry < 5 and len(responseTxt).__eq__(0):
        try:
            # logger.debug('...')
            # logger.debug('Navigating to | ' + url)

            response = requests.get(url)
            responseTxt = response.text
        except Exception as ex:
            retry += 1
            logger.error("make_http_request()=> " + str(ex))
            logger.error('...RETRYING...')
            time.sleep(3)

    return responseTxt


def get_product_urls(category):
    
    found_products = []
    
    try:
        # time.sleep(2)
        response_html = make_http_request(category['url'])
        if response_html != '':                
            soup = BeautifulSoup(response_html, "html.parser")
            found_products = soup.select('div[class="grid-uniform"]>div>div>a')
            
            next_page = soup.select_one('div[class="pagination"]>span[class="next"]>a')
                            
            while next_page:
                time.sleep(1)
                 
                response_html = make_http_request(base_url + next_page.attrs['href'])
                soup = BeautifulSoup(response_html, "html.parser")
                
                found_products.extend(soup.select('div[class="grid-uniform"]>div>div>a'))
                
                next_page = soup.select_one('div[class="pagination"]>span[class="next"]>a')
    except Exception as ex:
        logger.error("get_product_urls()=> " + str(ex))

    return found_products


def extract_product_info(url, category):
    try:
        time.sleep(1)
        
        response_html = make_http_request(url)
        
        if response_html != '':
            soup = BeautifulSoup(response_html, "html.parser")
            
            node = soup.select_one('script[id="ProductJson-product-template"]')
            if node:
                product_json = json.loads(node.next.strip())
                
                product = Product("manwomanhome")
                product.id = product_json['id']
                product.url = url
                product.title = product_json['title']
                product.brand = product_json['vendor']
                product.gender = category['gender']
                product.category = category['category']
                product.sub_category = category['sub_category']
                
                product.price = str(product_json['price_min'])
                product.price = product.price[:len(product.price)-2] + '.' + product.price[len(product.price)-2:]
                
                product.sale_price = str(product_json['price_max'])
                product.sale_price = product.sale_price[:len(product.sale_price)-2] + '.' + product.sale_price[len(product.sale_price)-2:]
                
                soup = BeautifulSoup(product_json['description'],"html.parser")
                if soup:
                    product.description = soup.text.strip()
                
                product.stock_availablity = product_json['available']
                product.imgs = product_json['images']
                
                for variant in product_json['variants']:
                    product.available_sizes_colors.append(variant['title'])
                
                return product
    except Exception as ex:
        logger.error('extract_product_info()=> ' + str(ex))
    
    return None


def write_headers_to_csv():
    try:
        with open(file_name, "a", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writeheader()
    except Exception as ex:
        logger.error("write_headers_to_csv()=> " + str(ex))


def export_to_csv(results):
    
    logger.debug("Exporting collected results so far, to CSV file.")
    logger.debug("File name => " + file_name)

    try:
        with open(file_name, "a", newline='' , encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)

            for d in results:
                try:
                    data = {'Date Scraped': d.date_time_scraped, 'Website': d.wesbite, 'Url': d.url, 'Gender': d.gender, 'Category': d.category, 'Sub Category': d.sub_category, 
                            'Title': d.title, 'Brand': d.brand,  'Price': d.price, 'Sale Price': d.sale_price, 'Description': d.description, 'Stock Availability': d.stock_availablity,
                            'Available Sizes & Colors': d.get_formatted_sizes_colors(), 'Reviews': d.reviews, 'Ratings': d.ratings, 'Images': d.get_formatted_imgs_urls() }
                    writer.writerow(data)
                except Exception as exc:
                    logger.error('exportToCSV(' + d.url + ')=> '+ str(exc))
                    logger.error(data)
    except Exception as ex:
        logger.error("exportToCSV()=> " + str(ex))



# start_scraping()
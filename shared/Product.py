from datetime import datetime
import json

class Product:
    def __init__(self, website):
        self.date_time_scraped = datetime.now().strftime("%m/%d/%YT%H:%M:%S")
        self.wesbite = website
        self.id = ''
        self.url = ''
        self.title = ''
        self.brand = ''
        self.gender = ''
        self.category = ''
        self.sub_category = ''
        self.price = ''
        self.sale_price = ''
        self.available_sizes_colors = []
        self.description = ''
        self.imgs = []
        self.reviews = []
        self.ratings = ''
        self.stock_availablity = "false"
        
    def get_formatted_sizes_colors(self):
        
        formatted_str = ''
        
        if self.available_sizes_colors != '':
            for i in self.available_sizes_colors:
                if formatted_str == '':
                    formatted_str = i
                else:
                    formatted_str += ', ' + i
        
        return formatted_str
                    
                    
    def get_formatted_imgs_urls(self):
        
        formatted_str = ''
        
        if self.imgs != '':
            for i in self.imgs:
                if formatted_str == '':
                    formatted_str = i
                else:
                    formatted_str += ', ' + i
                    
        return formatted_str
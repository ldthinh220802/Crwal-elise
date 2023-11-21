from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os

def get_all_links(products):
    links_products = []
    for product in products:
        a_element = product.find("a", {"class": "product photo product-item-photo"})
        if a_element:
            href = a_element['href']
            links_products.append(href)
    return links_products

def get_links(detail_product):
    all_links = []
    gallery_list = detail_product.find("div", class_="gallery-list")
    all_a_tags = gallery_list.find_all("a")
    for a_tag in all_a_tags:
        link = a_tag.find("img")["src"]
        if link:
            all_links.append(link)
    return all_links

def scrape_product_info(driver, link):
    obj = {}
    driver.get(link)
    # Sử dụng WebDriverWait để chờ đợi cho đến khi các phần tử xuất hiện
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-detail-infomation-sticky-parent")))
    
    html_detail = driver.page_source
    soup_detail = BeautifulSoup(html_detail, 'html.parser')
    detail_product = soup_detail.find("div", {"class": "row product-detail-infomation-sticky-parent"})
    try:
        obj['name'] = detail_product.find("h1", {"class": "product-name"}).text
        obj['code'] = detail_product.find("span", {"class": "value", "itemprop": "sku"}).text
        obj['image'] = get_links(detail_product)
        price = detail_product.find("span", {"class": "price"}).text
        # Sửa lỗi chính tả trong tên biến
        obj['price'] = price.replace(" VND", "")
    except:
        obj['name'] = None
        obj['code'] = None
        obj['image'] = None
        obj['price'] = None
    return obj

def main():
    driver = webdriver.Edge()
    driver.set_window_size(1920, 1080)

    for i in range(1, 9):
        print('lan thu', i)
        url = f"https://elise.vn/thoi-trang-nu?pdxqux={i}"
        driver.get(url)
        # Sử dụng WebDriverWait để chờ đợi cho đến khi các phần tử xuất hiện
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "products")))
        
        html_doc = driver.page_source
        soup = BeautifulSoup(html_doc, 'html.parser')

        all_products = soup.find("ol", {"class": "products list items product-items row"})
        product_elements = all_products.findAll("li", {"class": "item product product-item-info product-item col-12 col-xs-6 col-md-4 col-lg-3"})

        links_products = get_all_links(product_elements)
        data = []

        for link in links_products:
            obj = scrape_product_info(driver, link)
            print(obj)
            data.append(obj)

        df = pd.DataFrame(data)

        file_name = 'test.csv'
        if not os.path.isfile(file_name):
            df.to_csv(file_name, mode='w', header=True, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')

    print('crawl xong')
    driver.quit()

# Gọi hàm main để chạy chương trình
main()
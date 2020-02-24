import os, json
from selenium import webdriver
browser = webdriver.Firefox()
url = r'https://free-proxy-list.net'
browser.get(url)

click_next = r'proxylisttable_next.click()'
ip_list = {}

def find_elements(browser):
    even_elements = browser.find_elements_by_class_name('even')
    odd_elements = browser.find_elements_by_class_name('odd')
    return even_elements, odd_elements

def parse_elements(elements):
    for elem in elements:
        td_tags = elem.find_elements_by_tag_name('td')
        ip = td_tags[0].text
        port = td_tags[1].text
        ip_list[ip] = port

def store_ip(browser, click_next):
    ip_list = []
    even_elements, odd_elements = find_elements(browser)
    parse_elements(even_elements)
    parse_elements(odd_elements)
    browser.execute_script(click_next)

for i in range(15):
    store_ip(browser, click_next)

browser.close()

with open(os.path.join('data', 'proxies.json'), 'wt') as f:
    json.dump(ip_list, f, indent=4)
# Grab jpeg/png/mp4 from web site

import sys
import os
import time
import json
import argparse
import urlparse
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

def grab_jpeg(url):
    print 'Grabing JPEG images from %s' % url

    serverScheme = urlparse.urlparse(url).scheme
    serverUrl = urlparse.urlparse(url).netloc

    #log in if needed
    with open('passwd.json') as json_data:
        login = json.load(json_data)
        saved_username = login[serverUrl][0]
        saved_password = login[serverUrl][1]
        print saved_username + '/' + saved_password

    browser = webdriver.Chrome(executable_path='/usr/share/chromedriver')
    browser.set_page_load_timeout(90)
    browser.get(url)

    if saved_username and saved_password:
        username = browser.find_element_by_name('username')
        password = browser.find_element_by_name('password')

        if username is not None and password is not None:
            username.send_keys(saved_username)
            password.send_keys(saved_password)

            browser.find_element_by_xpath("//button[@type='submit']").click()

            time.sleep(5)
            browser.get(url)

    response = browser.page_source
    soup = BeautifulSoup(response, 'html.parser')

    if not os.path.exists(serverUrl):
        os.makedirs(serverUrl)

    count = 1
    for img in soup('img'):
        imgUrl =  img.get('src')
        if not imgUrl.startswith('http'):
            if imgUrl.startswith('/'):
                imgUrl = serverScheme + '://' + serverUrl + imgUrl
            else:
                imgUrl = serverScheme + '://' + serverUrl + '/' + imgUrl

        imgName = os.path.split(imgUrl)[1]
        if not imgName.endswith('gif') and not imgName.endswith('png'):

            print imgUrl

            if imgName.endswith('jpeg') or imgName.endswith('jpg'):
                imgName = imgName.split('.')[0] + '0' + str(count) + '.' + imgName.split('.')[1]
            else:
                imgName = imgName + '0' + str(count) + '.jpeg'

            if grabIt:
                myImg = requests.get(imgUrl)
                if len(myImg.content) > 20000:
                    with open(serverUrl + '/' + imgName, 'wb') as f:
                        f.write(myImg.content)
                else:
                    print 'ignored file %s' % imgName

        count += 1

    browser.quit()

parser = argparse.ArgumentParser()
parser.add_argument('-j', '--jpeg', action='store_true', help='grab all JPEG images')
parser.add_argument('-m', '--mp4', action='store_true', help='grab all mp4 videos')
parser.add_argument('-g', '--grab', action='store_true', help='grab it NOW')
parser.add_argument('-p', '--path', action='store', nargs=1, help='grab all mp4 videos')

options = parser.parse_args()
print options

grabIt = False
if options.grab:
    grabIt = True

if options.jpeg:
    grab_jpeg(options.path[0])

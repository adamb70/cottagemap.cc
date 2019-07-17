import time

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

import settings
from data_objects import LateOffer
from db_handler import SQL_Handler


class SpiderSettings:
    defaults = {'wifi': True, 'parking': False, 'washing': False, 'kingsize': False, 'pool': False, 'hottub': False}

    def __init__(self):
        self.__dict__ = self.defaults

    def __getattr__(self, item):
        return self.__dict__.get(item.lower(), False)

    def __setattr__(self, key, value):
        key = key.lower()
        self.__dict__[key] = value
        super(SpiderSettings, self).__setattr__(key, value)


class Spider:
    region_tables = {
        'north east england': "northeastengland",
        'north west england': "northwestengland",
        'central england': "centralengland",
        'north wales': "northwales",
        'south wales': "southwales",
        'eastern central england': "easterncentralengland",
        'eastern england & east anglia': "eastanglia",
        'south west england': "southwestengland",
        'south and south east england': "southeastengland",
        'south west scotland': "southwestscotland",
        'south east scotland': "southeastscotland",
        'west central scotland': "westcentralscotland",
        'east central scotland': "eastcentralscotland",
        'scottish highlands': "scottishhighlands",
        'northern ireland': "northernireland",
    }

    def __init__(self):
        self.sql = SQL_Handler()
        self.settings = SpiderSettings()

    def parse_results(self, search_results: WebElement):
        offers = []
        for cottage in search_results.find_elements_by_class_name('holiday-cottage-item'):
            offer = LateOffer()
            offer.lat, offer.lon = cottage.find_element_by_class_name('mapLatLong').get_attribute(
                'textContent').strip().split(',')

            title_info = cottage.find_element_by_css_selector('h3>a')
            offer.title = title_info.text

            offer.url = title_info.get_attribute('href')
            offer.ref = offer.url.split('-ref')[-1]
            offer.slug = offer.url.split('/')[-1].split('-ref')[0]

            offer.location = cottage.find_element_by_css_selector('.loc-container>a').text
            offer.description = cottage.find_element_by_css_selector('.cottage-img .para').text

            regular_price = cottage.find_element_by_css_selector('.price-from-sec>.price').text.replace('£', '').replace(' all year', '')
            offer.weekly_low = int(regular_price.split(' to ')[0])
            offer.weekly_high = int(regular_price.split(' to ')[-1])

            meta = cottage.find_element_by_class_name('products-meta').text.lower().strip().split('\n')[0].split('|')
            offer.sleeps = meta[0].strip()
            offer.bedrooms = meta[1].strip()
            offer.dog = meta[2].strip() != 'no'
            offer.child = meta[3].strip() != 'no'
            offer.wifi = meta[4].strip() != 'no'

            # Late offer
            offer_details = cottage.find_element_by_css_selector('.lao-strip .offer-block')
            try:
                offer.late_savings_tag = offer_details.find_element_by_class_name('tag').text
            except NoSuchElementException:
                offer.late_savings_tag = ""
            offer.late_offer = offer_details.text.replace(offer.late_savings_tag, '')
            offer.late_price = int(offer.late_offer.split(', £')[-1])
            offer.late_nights = int(offer.late_offer.split(' for ')[-1].split(' night')[0])

            offers.append(offer)
        return offers

    def save_offers(self, offers, table_name):
        row = """INSERT INTO {TABLE_NAME} (ID, title, lat, lon, location, url, slug, ref, description,
              weekly_low, weekly_high, sleeps, bedrooms, dog, child, wifi, late_offer, late_nights,
              late_price, late_savings_tag ) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
              %s,%s,%s,%s)""".format(TABLE_NAME=table_name)

        for offer in offers:
            self.sql.cur.execute(row, (
                offer.title, offer.lat, offer.lon, offer.location, offer.url, offer.slug, offer.ref, offer.description,
                offer.weekly_low, offer.weekly_high, offer.sleeps, offer.bedrooms, offer.dog, offer.child, offer.wifi,
                offer.late_offer, offer.late_nights, offer.late_price, offer.late_savings_tag
            ))

        self.sql.commit()

    def populate_table(self, region):
        try:
            TABLE_NAME = self.region_tables[region]
        except KeyError:
            return 'Not a valid region'

        chrome_options = Options()
        chrome_options.binary_location = settings.GOOGLE_CHROME_BIN
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(executable_path=settings.CHROMEDRIVER_PATH, options=chrome_options)

        # Request search page
        driver.get('https://www.independentcottages.co.uk/cottageSearch.php#search_filter')

        # Open filters
        driver.find_element_by_id('opener-btn-side').click()
        while len(driver.find_elements_by_css_selector('.accordion.active')) > 0:
            try:
                driver.find_element_by_css_selector('.accordion.active').click()
                time.sleep(0.7)  # wait for animation to avoid misclicks
            except (ElementClickInterceptedException, ElementNotInteractableException):
                pass

        # Fill fields
        form = driver.find_element_by_id('update-results')
        form.find_element_by_name('advUserSearch').send_keys(region)
        Select(form.find_element_by_name('sleeps')).select_by_value('2')
        form.find_element_by_id('searchTypeb').click()  # Select late only deals

        if self.settings.WIFI:
            form.find_element_by_id('broadband').click()
        if self.settings.PARKING:
            form.find_element_by_id('offRoadParking').click()
        if self.settings.WASHING:
            form.find_element_by_id('washingMachine').click()
        if self.settings.KINGSIZE:
            form.find_element_by_id('kingsizeBed').click()
        if self.settings.POOL:
            form.find_element_by_id('swimmingPool').click()
        if self.settings.HOTTUB:
            form.find_element_by_id('hotTub').click()

        # Submit form
        form.find_element_by_class_name('btn-orange').click()

        offers = []
        while True:
            results = driver.find_element_by_id('start-of-results')

            if results.text.lower().startswith('sorry'):
                # No results found
                print(f'No results for {region}')
                break

            offers.extend(self.parse_results(results))

            # move to next page
            try:
                paginate_next = driver.find_element_by_id('pagination-list').find_elements_by_css_selector('li')[
                    -1].find_element_by_css_selector('a')
                if paginate_next.text.strip().lower().startswith('next'):
                    paginate_next.click()
                else:
                    break
            except:
                # No pagination
                break

        self.sql.create_table(table_name=TABLE_NAME)
        self.sql.clear_table(table_name=TABLE_NAME)

        self.save_offers(offers, table_name=TABLE_NAME)

        self.sql.close()


for region in list(Spider.region_tables.keys())[0:1]:
    print('Gathering late deals from', region)
    spider = Spider()
    spider.populate_table(region)

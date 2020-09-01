import os
import time
import urllib.request
from urllib.parse import urlparse
from multiprocessing import Pool

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, \
    NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import settings
from data_objects import OfferRow, REGION_TABLES, empty_b64_jpg
from db_handler import MySQL_Handler, Postgres_Handler


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
    sql = None

    def __init__(self, use_postgres=True, driver='chrome'):
        if use_postgres:
            self.sql_handler = Postgres_Handler
        else:
            self.sql_handler = MySQL_Handler
        if driver == 'chrome':
            chrome_options = Options()
            chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN', '')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            if os.environ.get('USE_DEV_SHM', False):
                chrome_options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH', 'chromedriver.exe'),
                                           options=chrome_options)
        elif driver == 'firefox':
            firefox_options = FirefoxOptions()
            firefox_options.headless = True
            self.driver = webdriver.Firefox(options=firefox_options, firefox_binary=os.environ.get('FIREFOX_BIN'),
                                            executable_path=os.environ.get('GECKODRIVER_PATH'))
        else:
            raise ValueError(f'Driver {driver} is not of type `firefox` for `chrome`.')

        self.driver.set_window_size(1920, 1080)
        self.search_setup_complete = False
        self.settings = SpiderSettings()

    def connect_db(self):
        self.sql = self.sql_handler()

    def disconnect_db(self):
        self.sql.close()

    def quit_driver(self):
        self.driver.quit()

    def parse_results(self, search_results: WebElement, driver, get_b64_images=False):
        offers = []
        for cottage in search_results.find_elements_by_class_name('holiday-cottage-item'):
            offer = OfferRow()
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
            try:
                offer.weekly_low = int(regular_price.split(' to ')[0])
            except ValueError:
                # Failed because price is text
                offer.weekly_low = 0
            try:
                offer.weekly_high = int(regular_price.split(' to ')[-1])
            except ValueError:
                # Failed because price is text
                offer.weekly_high = 0

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

            # Get image url
            img = cottage.find_element_by_css_selector(f'#img-{offer.ref} img')
            base_url = urlparse(driver.current_url).netloc
            img_url = img.get_attribute('data-src')
            offer.img_url = "https://" + base_url + img_url

            if get_b64_images:
                # Image
                js = """
                let canvas = document.createElement('canvas');
                let img = document.querySelector('#img-{ref} img');
                img.scrollIntoView();
                canvas.id = 'canvas-{ref}';
                
                // wait for image to load before adding it to canvas
                img.onload = function() {{
                    // using canvas to generate a b64 dataurl without having to request the image a second time to download
                    canvas.width = img.width;
                    canvas.height = img.height;
                    document.body.appendChild(canvas);
                    let ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    let data = canvas.toDataURL('image/jpeg', 1.0);
                    let output = document.createElement('div');
                    output.id = 'output-{ref}';
                    output.setAttribute('dataurl', data);
                    img.parentNode.insertBefore(output, output.nextSibling);
                }};
                // if image has already loaded before attaching the listener, manually fire it
                if (img.complete && img.naturalHeight !== 0) {{
                    let evt = document.createEvent('Event');
                    evt.initEvent('load', false, false);
                    img.dispatchEvent(evt);
                }}
                """.format(ref=offer.ref)
                driver.execute_script(js)

                # Download image as base64
                try:
                    data_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, f'output-{offer.ref}')))
                    dataurl = data_elem.get_attribute('dataurl')
                    if dataurl == empty_b64_jpg:
                        # image wasn't loaded properly
                        dataurl = None
                except TimeoutException:
                    dataurl = None

                if dataurl:
                    response = urllib.request.urlopen(dataurl)
                    offer.image = response.read()

            offers.append(offer)
        return offers

    def search(self, region):
        # Request search page
        self.driver.get('https://www.independentcottages.co.uk/cottageSearch.php#search_filter')

        # Open filters
        try:
            self.driver.find_element_by_css_selector('#search-form-container[style*="display: none;"]')
            self.driver.find_element_by_id('opener-btn-side').click()
        except NoSuchElementException:
            # Don't need to open the search form
            pass

        while len(self.driver.find_elements_by_css_selector('.accordion.active')) > 0:
            try:
                self.driver.find_element_by_css_selector('.accordion.active').click()
                time.sleep(0.7)  # wait for animation to avoid misclicks
            except (ElementClickInterceptedException, ElementNotInteractableException):
                pass

        form = self.driver.find_element_by_id('update-results')
        if not self.search_setup_complete:
            # Fill fields
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
            self.search_setup_complete = True
        else:
            # Clear the previous search request before entering a new one
            form.find_element_by_name('advUserSearch').clear()
            form.find_element_by_name('advUserSearch').send_keys(region)
        form.find_element_by_class_name('btn-orange').click()

    def populate_table(self, region, get_b64_images=False):
        try:
            TABLE_NAME = REGION_TABLES[region]
        except KeyError:
            return 'Not a valid region'

        # Perform search
        self.search(region)

        offers = []
        while True:
            results = self.driver.find_element_by_id('start-of-results')

            if results.text.lower().startswith('sorry'):
                # No results found
                print(f'No results for {region}')
                break

            offers.extend(self.parse_results(results, self.driver, get_b64_images))

            # move to next page
            try:
                paginate_next = self.driver.find_element_by_id('pagination-list').find_elements_by_css_selector('li')[
                    -1].find_element_by_css_selector('a')
                if paginate_next.text.strip().lower().startswith('next'):
                    paginate_next.click()
                else:
                    break
            except:
                # No pagination
                break

        print(f'saving {len(offers)} items to db...')
        self.connect_db()
        self.sql.clear_table(table_name=TABLE_NAME)
        self.sql.save_offers(offers, table_name=TABLE_NAME)
        self.disconnect_db()


def crawl(region, use_postgres=True, get_b64_images=False):
    print('Gathering late deals from', region)
    spider = Spider(use_postgres=use_postgres, driver=os.environ.get('DRIVER_TYPE', 'chrome'))
    spider.populate_table(region, get_b64_images=get_b64_images)
    spider.quit_driver()


def multiprocess_crawl(regions: list, process_count=4, use_postgres=True, get_b64_images=False):
    from itertools import repeat

    p = Pool(process_count)
    p.starmap(crawl, list(zip(regions, repeat(use_postgres), repeat(get_b64_images))))


if __name__ == '__main__':
    print(f'Starting crawl with {settings.PROCESS_COUNT} processes')
    multiprocess_crawl(list(REGION_TABLES.keys()), settings.PROCESS_COUNT, use_postgres=True)
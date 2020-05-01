from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from Config import params_config, db_config
from ScrapingTools.netkeiba_info_scraper import RaceInfoScraper

import warnings
warnings.filterwarnings('ignore')


def initialize_chrome_driver(parameters):
    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    driver = Chrome(executable_path=parameters['DRIVER_DIR'], chrome_options=chrome_options)
    driver.set_page_load_timeout(parameters['PAGE_LOAD_TIMEOUT'])
    driver.maximize_window()
    return driver


def main():
    parameters = params_config.parameters
    db_params = db_config.db_params
    driver = initialize_chrome_driver(parameters)
    ris = RaceInfoScraper(parameters, db_params, driver)
    
    print('Scrape race master and prior table info')
    ris.get_race_master_and_table_info()

    print('Scrape race result info')
    ris.get_race_result_info()

    print('Scrape past 5 race result info')
    ris.get_past_5_race_result_info()

    print('Finish scraping.')
    driver.quit()


if __name__ == '__main__':
    main()

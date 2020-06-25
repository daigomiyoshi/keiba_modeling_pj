from Config import params_config, db_config
from ScrapingTools.netkeiba_info_scraper import RaceInfoScraper

import warnings
warnings.filterwarnings('ignore')



def main():
    parameters = params_config.parameters
    db_params = db_config.db_params
    ris = RaceInfoScraper(parameters, db_params)
    
    print('Scrape race master and prior table info \n')
    ris.get_race_master_and_table_info()

    print('Scrape race result info \n')
    ris.get_race_result_info()

    print('Scrape past 5 race result info \n')
    ris.get_past_5_race_result_info()

    print('Finish scraping.')
    ris.quit_driver


if __name__ == '__main__':
    main()

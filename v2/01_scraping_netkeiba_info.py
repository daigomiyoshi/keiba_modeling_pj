from Config import params_config, db_config
from ScrapingTools.NetKeibaInfoScraper import RaceInfoScraper

import warnings
warnings.filterwarnings('ignore')


def main():
    parameters = params_config.parameters
    db_params = db_config.db_params

    ris = RaceInfoScraper(parameters, db_params)
    print('Scrape race master and prior table info')
    ris.get_race_master_and_table_info()

    print('Scrape race result info')

    print('Finish scraping.')


if __name__ == '__main__':
    main()

from Simulator import preprocess, modeling, simulate_profit

import warnings
warnings.filterwarnings('ignore')


def main():
    print('Preprocess the data for modeling. \n')
    datamart = preprocess.preprocess_datamart()
    print('Fit the model into data. \n')
    y_test_pred = modeling.fit(datamart)
    print('Finish. \n')


if __name__ == "__main__":
    main()

import pandas as pd
import datetime as dt
import os

class db:
    def __init__(self):

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.transactions = self.transaction_init()
        self.cc = pd.read_csv(os.path.join(self.BASE_DIR, 'db', 'country_codes.csv'), index_col=0)
        self.customers = pd.read_csv(os.path.join(self.BASE_DIR, 'db', 'customers.csv'), index_col=0)
        self.prod_info = pd.read_csv(os.path.join(self.BASE_DIR, 'db', 'prod_cat_info.csv'))

    def transaction_init(self):
        dfs = []

        src = os.path.join(self.BASE_DIR, 'db', 'transactions')

        for filename in os.listdir(src):
            dfs.append(pd.read_csv(os.path.join(src, filename), index_col=0))

        transactions = pd.concat(dfs)

        def convert_dates(x):
            try:
                return dt.datetime.strptime(x, '%d-%m-%Y')
            except:
                return dt.datetime.strptime(x, '%d/%m/%Y')

        transactions['tran_date'] = transactions['tran_date'].apply(convert_dates)

        return transactions

    def merge(self):
        df = self.transactions.join(self.prod_info.drop_duplicates(subset=['prod_cat_code'])
        .set_index('prod_cat_code')['prod_cat'],on='prod_cat_code',how='left')

        df = df.join(self.prod_info.drop_duplicates(subset=['prod_sub_cat_code'])
        .set_index('prod_sub_cat_code')['prod_subcat'],on='prod_subcat_code',how='left')

        df = df.join(self.customers.join(self.cc,on='country_code')
        .set_index('customer_Id'),on='cust_id')

        self.merged = df

    def merged_df(self, start_date, end_date):

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        dff = self.merged[
            (self.merged["tran_date"] >= start_date) &
            (self.merged["tran_date"] <= end_date)
        ].copy()

        dff = dff[dff["total_amt"] > 0]

        return dff
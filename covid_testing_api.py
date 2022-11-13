# -*- coding: utf-8 -*-
from fastapi import FastAPI, Query
import json
from typing import Optional
import pandas as pd

app = FastAPI()


# read in csv
url='https://opendata.ecdc.europa.eu/covid19/testing/csv/data.csv'
covid_data = pd.read_csv(url)
# define countries for subsetting
# share function with Jupyter notebook
countries = ["Denmark", "Germany", "Italy", "Spain", "Sweden"]
covid_data_subset = covid_data[covid_data['country'].isin(countries)].copy()
covid_data_subset['dates'] = pd.to_datetime(covid_data_subset['year_week'] +'-1', format="%Y-W%W-%w")
covid_data_subset['months'] = covid_data_subset['dates'].dt.year.astype(str) + "-" + covid_data_subset['dates'].dt.month.astype(str)
covid_data_subset.set_index('dates', inplace=True)
covid_summary = covid_data_subset.groupby(['country_code', 'country', 'months']).resample('M').sum().reset_index()

country_list = covid_summary['country_code'].unique().tolist()


@app.get("/country/{country_code}")
async def get_country_data(country_code: str = Query()):
    if country_code in country_list:
        country_data = covid_summary[covid_summary['country_code'] == country_code]
        
        json_format = country_data.to_json(orient='split', date_format="iso")
        return json.loads(json_format)
    
    else:
        return {"message": "not valid country"}
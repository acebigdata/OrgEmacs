import pandas as pd
import numpy as np
import sqlite3
from os.path import dirname, join, abspath
import os

from bokeh.plotting import figure
from bokeh.models.annotations import LabelSet
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, TableColumn, CustomJS
from bokeh.models.widgets import Select, PreText, Button, MultiSelect, DataTable, TableColumn, NumberFormatter
from bokeh.layouts import layout, row, column
from bokeh.embed import components

from flask import Flask,url_for


#Load datafiles first
DATA_DIR_OUT = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'tmp'))

filenames = next(os.walk(DATA_DIR_OUT))[2]
NEW_tables = [f.split(".csv")[0] for f in filenames]
selection_db={}

def replace_nans(data):
    for key in data:
        data[key] = ['NaN' if pd.isnull(value) else value for value in data[key]]
    return data


for table in NEW_tables:
    selection_db[table] = pd.read_csv(join(DATA_DIR_OUT, table+".csv"))

#Widget for Multi-Selecting Metrics

table_list = NEW_tables
table_keys = list(selection_db.keys())
year_list = sorted(list(set(selection_db["Total Revenue"]["Year"])))

# table_list = ['Total Revenue', 'COGS', 'COGS Ratio', 'Gross Profit', 'Gross Profit Margin',
#  'SG&A', 'SG&A Ratio', 'R&D', 'R&D Ratio', 'Total Other OPEX', 'Total Other OPEX Ratio',
#  'Operating Income', 'Operating Income Margin', 'EBT', 'EBT Margin', 'EBIT', 'EBIT Margin',
#  'EBITDA', 'EBITDA Margin', 'Income Taxes', 'NOPAT', 'NOPAT Margin', 'Cash And Equivalents',
#  'Total Receivables', 'DSO', 'Short Term Investments', 'Inventory', 'Inventory Turnover',
#  'Total Current Assets', 'Net Property, Plant & Equipment', 'Fixed Asset Turnover',
#  'Goodwill', 'Total Assets', 'Accounts Payable', 'DPO', 'Total Current Liabilities',
#  'Long-Term Debt', 'Total Liabilities', 'Total Equity', 'Invested Capital', 'CTR', 'Total Liabilities And Equity']

region_list = ['All','North America', 'Europe', 'Asia-Pacific', 'Emerging', 'Rest of World']

country_list = ['All','United States','Sweden','China','Germany', 'Argentina', 'Australia', 'Austria', 'Bahrain', 'Bangladesh', 'Barbados', 'Belgium',
 'Bermuda', 'Botswana', 'Brazil', 'Cambodia', 'Canada', 'Cayman Islands', 'Channel Islands', 'Chile',
 'Colombia', 'Croatia', 'Curaçao', 'Cyprus', 'Czech Republic', 'Denmark', 'Egypt', 'Estonia', 'Finland',
 'France', 'Ghana', 'Gibraltar', 'Greece', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia',
 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait',
 'Lebanon', 'Luxembourg', 'Malaysia', 'Malta', 'Marshall Islands', 'Mexico', 'Monaco', 'Morocco', 'Netherlands', 'New Zealand',
 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palestinian Authority', 'Panama', 'Papua New Guinea', 'Peru', 'Philippines',
 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Saudi Arabia', 'Senegal', 'Singapore', 'Slovakia', 'Slovenia', 'South Africa',
 'South Korea', 'Spain', 'Sri Lanka',  'Switzerland', 'Taiwan', 'Thailand', 'Togo', 'Trinidad & Tobago', 'Tunisia', 'Turkey',
 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Uruguay', 'Venezuela', 'Vietnam', 'Zambia', 'Zimbabwe']

sector_list = ['All','Advertising', 'Aerospace', 'Agriculture Equipment', 'Airlines', 'Aluminum', 'Auto OEM',
 'Base Metal', 'Beverage', 'Broadcasting', 'Chemicals', 'Construction', 'Education', 'Energy', 'Entertainment',
 'Environmental', 'Equipment Mech./Industrial', 'FiNAcial Services', 'Food', 'Freight & Logistics', 'HR', 'Health Care',
 'Highways and Railtracks', 'Holding Company', 'Hotel', 'Insurance', 'Marine', 'Medical Devices', 'Mining', 'Oil & Gas',
 'Online Retail', 'Other Services', 'Packaging', 'Paper & Pulp', 'Personal & Household', 'Pharma', 'Precious Metal', 'Printing',
 'Publishing', 'Real Estate', 'Restaurants', 'Retail', 'SW & Computer Services', 'Steel', 'Tech HW Equipment', 'Telecome Operators',
 'Textiles', 'Tier 1', 'Trading & Distribution', 'Truck OEM', 'Utilities', 'White Goods']

source = ColumnDataSource(data=dict())
full_source = ColumnDataSource(data=dict())


select_data={}
#Widgets for loading selections
def load_selection():
    global mask_region
    global mask_country
    global mask_sector
    global final_mask
    global show_mask

    select_metric = select_table.value


    if select_region.value == "All" and select_country.value == "All" and select_sector.value == "All":
        mask_region = pd.Series([True] * len(selection_db[select_metric]))
        mask_country = pd.Series([True] * len(selection_db[select_metric]))
        mask_sector = pd.Series([True] * len(selection_db[select_metric]))
    elif select_region.value != "All" and select_country.value == "All" and select_sector.value == "All":
        mask_region = selection_db[select_metric]["Region"] == select_region.value
        mask_country = pd.Series([True] * len(selection_db[select_metric]))
        mask_sector = pd.Series([True] * len(selection_db[select_metric]))
    elif select_region.value == "All" and select_country.value != "All" and select_sector.value == "All":
        mask_region = pd.Series([True] * len(selection_db[select_metric]))
        mask_country = selection_db[select_metric]["Country"] == select_country.value
        mask_sector = pd.Series([True] * len(selection_db[select_metric]))
    elif select_region.value == "All" and select_country.value == "All" and select_sector.value != "All":
        mask_region = pd.Series([True] * len(selection_db[select_metric]))
        mask_country = pd.Series([True] * len(selection_db[select_metric]))
        mask_sector = selection_db[select_metric]["AV Sector"] == select_sector.value
    elif select_region.value != "All" and select_country.value != "All" and select_sector.value == "All":
        mask_region = selection_db[select_metric]["Region"] == select_region.value
        mask_country = selection_db[select_metric]["Country"] == select_country.value
        mask_sector = pd.Series([True] * len(selection_db[select_metric]))
    elif select_region.value != "All" and select_country.value == "All" and select_sector.value != "All":
        mask_region = selection_db[select_metric]["Region"] == select_region.value
        mask_country = pd.Series([True] * len(selection_db[select_metric]))
        mask_sector = selection_db[select_metric]["AV Sector"] == select_sector.value
    elif select_region.value == "All" and select_country.value != "All" and select_sector.value != "All":
        mask_region = pd.Series([True] * len(selection_db[select_metric]))
        mask_country = selection_db[select_metric]["Country"] == select_country.value
        mask_sector = selection_db[select_metric]["AV Sector"] == select_sector.value
    elif select_region.value != "All" and select_country.value != "All" and select_sector.value != "All":
        mask_region = selection_db[select_metric]["Region"] == select_region.value
        mask_country = selection_db[select_metric]["Country"] == select_country.value
        mask_sector = selection_db[select_metric]["AV Sector"] == select_sector.value

    final_mask = (mask_region & mask_country & mask_sector)
    year_mask = selection_db[select_metric]["Year"] == select_year.value
    show_mask = final_mask & year_mask

    select_data_1 = selection_db[select_metric][show_mask]
    select_data_1 = replace_nans(select_data_1)


    source.data = {
        'company_name': select_data_1["Company Name"],
        'ticker': select_data_1["Exchange:Ticker"],
        'country': select_data_1["Country"],
        'region': select_data_1["Region"],
        'av_sector': select_data_1["AV Sector"],
        'year': select_data_1["Year"],
        'metric': select_data_1[select_metric],
    }

    select_data_2 = selection_db[select_metric][final_mask]
    select_data_2["Company Name"] = select_data_2["Company Name"].str.strip()
    select_data_2["Company Name"] = select_data_2["Company Name"].str.replace(',', '')
    select_data_2 = replace_nans(select_data_2)
    full_source.data = {
        'company_name': select_data_2["Company Name"],
        'ticker': select_data_2["Exchange:Ticker"],
        'country': select_data_2["Country"],
        'region': select_data_2["Region"],
        'av_sector': select_data_2["AV Sector"],
        'year': select_data_2["Year"],
        'metric': select_data_2[select_metric],
    }

    df_groupbyyear_min = select_data_1[select_metric].min()
    df_groupbyyear_mean = select_data_1[select_metric].mean()
    df_groupbyyear_max = select_data_1[select_metric].max()
    df_groupbyyear_median = select_data_1[select_metric].median()
    df_groupbyyear_bottom_20 = select_data_1[select_metric].quantile(0.2)
    df_groupbyyear_top_20 = select_data_1[select_metric].quantile(0.8)

    source_stat.data = {
        'min': [df_groupbyyear_min],
        'max': [df_groupbyyear_max],
        'mean': [df_groupbyyear_mean],
        'median': [df_groupbyyear_median],
        'top_20': [df_groupbyyear_top_20],
        'bottom_20': [df_groupbyyear_bottom_20],
    }

    return select_data_2

def update(attr, old, new):
    main_display.children[1] = load_selection()

#Widgets for update button
select_df = Button(label="Load Selected Data", button_type="primary")
select_df.on_click(load_selection)

#Widgets for download button
# def download_df():
#     newpath = r'C:\\AVA\\'
#     if not os.path.exists(newpath):
#         os.makedirs(newpath)
#     load_selection().to_csv(join(newpath,"results.csv"), index=False)
#
download_button = Button(label="Download", button_type="success")
# download_button.on_click(download_df)
download_button.callback = CustomJS(args=dict(source=full_source), code=open(join(dirname(__file__), "download.js")).read())
#Widgets for data table

columns = [
    TableColumn(field="company_name", title="Company Name"),
    TableColumn(field="year", title="Year"),
    TableColumn(field="metric", title="Metrics", formatter=NumberFormatter(format="0,0.00"))
]

data_table = DataTable(source=source, columns=columns, width=800, editable=True)

#Widgets for data table 2
source_stat = ColumnDataSource(data=dict())
columns = [
    TableColumn(field="min", title="Min Value", formatter=NumberFormatter(format="0,0.00")),
    TableColumn(field="max", title="Max Value", formatter=NumberFormatter(format="0,0.00")),
    TableColumn(field="mean", title="Average Value", formatter=NumberFormatter(format="0,0.00")),
    TableColumn(field="median", title="Median Value", formatter=NumberFormatter(format="0,0.00")),
    TableColumn(field="top_20", title="Top 20%", formatter=NumberFormatter(format="0,0.00")),
    TableColumn(field="bottom_20", title="Bottom 20%", formatter=NumberFormatter(format="0,0.00")),
]
stat_table = DataTable(source=source_stat, columns=columns, width=800, height=80,editable=True)


#Widgets for table selection
def update_table_selection(attr, old, new):
    global table_name
    table_name = select_table.value

select_table = Select(value=table_list[0],options=table_list)
select_table.on_change("value",update)
table_name = select_table.value

#Widgets for region selection
def update_region_selection(attr, old, new):
    global region_name
    region_name = select_region.value

select_region = Select(value="All",options=region_list)
select_region.on_change("value",update)
region_name = select_region.value

#Widgets for country selection
def update_country_selection(attr, old, new):
    global country_name
    country_name = select_country.value

select_country = Select(value="All", options=country_list)
select_country.on_change("value", update)
country_name = select_country.value

#Widgets for sector selection
def update_sector_selection(attr, old, new):
    global sector_name
    sector_name = select_sector.value

select_sector = Select(value="All", options=sector_list)
select_sector.on_change("value", update)
sector_name = select_sector.value

region_country_sector_select_msg = PreText(width=500, height=50)

#Widgets for year selection
#Widgets for sector selection
def update_year_selection(attr, old, new):
    global year_name
    year_name = select_year.value

select_year = Select(value="All", options=year_list)
select_year.on_change("value", update)
year_name = select_year.value

#Display widgets
main_select = column(select_table, select_region, select_country, select_sector, select_year, select_df, download_button)
main_display = column(data_table, stat_table)
lay_out = row(main_select, main_display)
# lay_out = column(lay_out, f)
# lay_out = layout([[select_table],[select_region],[select_country],[select_sector],[select_df], [msg_title], [msg_info]])
curdoc().add_root(lay_out)
# update()

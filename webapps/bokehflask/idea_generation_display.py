import pandas as pd
import numpy as np
import sqlite3
from os.path import dirname, join
import os
import webbrowser

from bokeh.plotting import figure
from bokeh.models.annotations import LabelSet
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, TableColumn, CustomJS
from bokeh.models.widgets import Select, PreText, Button, MultiSelect, DataTable, TableColumn, NumberFormatter, Slider
from bokeh.layouts import layout, row, column
from bokeh.embed import components


## Function to convert wide to long
def gather( df, key, value, cols ):
    id_vars = [ col for col in df.columns if col not in cols ]
    id_values = cols
    var_name = key
    value_name = value
    return pd.melt(df, id_vars, id_values, var_name, value_name)

#Load datafiles first
DATA_DIR_FALL_WIDE = join(dirname(__file__), 'ideagen','fall','wide')
DATA_DIR_RISE_WIDE = join(dirname(__file__), 'ideagen','rise', 'wide')
DATA_DIR_FALL_LONG = join(dirname(__file__), 'ideagen','fall','long')
DATA_DIR_RISE_LONG = join(dirname(__file__), 'ideagen','rise', 'long')

#Widgets for falling metrics
filenames_fall = next(os.walk(DATA_DIR_FALL_WIDE))[2]
fall_tables = [f.split(".csv")[0] for f in filenames_fall]

filenames_rise = next(os.walk(DATA_DIR_RISE_WIDE))[2]
rise_tables = [f.split(".csv")[0] for f in filenames_rise]

fall_db_long={}
fall_db_wide={}

for table in fall_tables:
    # fall_db_long[table] = pd.read_csv(join(DATA_DIR_FALL_LONG, table+".csv"))
    fall_db_wide[table] = pd.read_csv(join(DATA_DIR_FALL_WIDE, table+".csv"))

#Widgets for rising metrics
filenames_rise = next(os.walk(DATA_DIR_RISE_WIDE))[2]
rise_tables = [f.split(".csv")[0] for f in filenames_rise]
rise_db_long={}
rise_db_wide={}

for table in rise_tables:
    # rise_db_long[table] = pd.read_csv(join(DATA_DIR_RISE_LONG, table+".csv"))
    rise_db_wide[table] = pd.read_csv(join(DATA_DIR_RISE_WIDE, table+".csv"))

#Widget for Multi-Selecting Metrics

fall_list = list(fall_db_wide.keys())
rise_list = list(rise_db_wide.keys())

# fall_table_keys = list(fall_db_long.keys())


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

info_list=["Company Name", "Exchange:Ticker", "Country", "Region", "AV Industry", "AV Sector"]

source_fall = ColumnDataSource(data=dict())
source_rise = ColumnDataSource(data=dict())


#Widgets for loading selections
def load_selection():
    global mask_region
    global mask_country
    global mask_sector
    global final_mask

    select_fall_metric = select_fall_table.value
    select_rise_metric = select_rise_table.value

    inspection_years = select_year.value
    year_len = len(inspection_years)
    first_inspect_year_index = full_year_list.index(inspection_years[0])
    inspection_year_previous = full_year_list[first_inspect_year_index-1:first_inspect_year_index+year_len-1]

    full_table_fall = fall_db_wide[select_fall_metric]
    full_table_rise = rise_db_wide[select_rise_metric]

    full_columns = info_list + list(sorted(set(inspection_year_previous + inspection_years)))
    show_columns = info_list + select_year.value
    full_table_fall = full_table_fall[full_columns]
    full_table_rise = full_table_rise[full_columns]

    alpha = slider.value

    if select_region.value == "All" and select_country.value == "All" and select_sector.value == "All":
        mask_region = pd.Series([True] * len(full_table_fall))
        mask_country = pd.Series([True] * len(full_table_fall))
        mask_sector = pd.Series([True] * len(full_table_fall))
    elif select_region.value != "All" and select_country.value == "All" and select_sector.value == "All":
        mask_region = full_table_fall["Region"] == select_region.value
        mask_country = pd.Series([True] * len(full_table_fall))
        mask_sector = pd.Series([True] * len(full_table_fall))
    elif select_region.value == "All" and select_country.value != "All" and select_sector.value == "All":
        mask_region = pd.Series([True] * len(full_table_fall))
        mask_country = full_table_fall["Country"] == select_country.value
        mask_sector = pd.Series([True] * len(full_table_fall))
    elif select_region.value == "All" and select_country.value == "All" and select_sector.value != "All":
        mask_region = pd.Series([True] * len(full_table_fall))
        mask_country = pd.Series([True] * len(full_table_fall))
        mask_sector = full_table_fall["AV Sector"] == select_sector.value
    elif select_region.value != "All" and select_country.value != "All" and select_sector.value == "All":
        mask_region = full_table_fall["Region"] == select_region.value
        mask_country = full_table_fall["Country"] == select_country.value
        mask_sector = pd.Series([True] * len(full_table_fall))
    elif select_region.value != "All" and select_country.value == "All" and select_sector.value != "All":
        mask_region = full_table_fall["Region"] == select_region.value
        mask_country = pd.Series([True] * len(full_table_fall))
        mask_sector = full_table_fall["AV Sector"] == select_sector.value
    elif select_region.value == "All" and select_country.value != "All" and select_sector.value != "All":
        mask_region = pd.Series([True] * len(full_table_fall))
        mask_country = full_table_fall["Country"] == select_country.value
        mask_sector = full_table_fall["AV Sector"] == select_sector.value
    elif select_region.value != "All" and select_country.value != "All" and select_sector.value != "All":
        mask_region = full_table_fall["Region"] == select_region.value
        mask_country = full_table_fall["Country"] == select_country.value
        mask_sector = full_table_fall["AV Sector"] == select_sector.value

    final_mask = (mask_region & mask_country & mask_sector)
    # print(final_mask)
    #Filtered data frame
    select_data_fall = full_table_fall[final_mask]
    select_data_rise = full_table_rise[final_mask]

    # print(select_data)
    #Filtered data frame
    temp_data_fall = select_data_fall
    temp_data_rise = select_data_rise

    for i, j in zip (inspection_years, inspection_year_previous):
        temp_data_fall = temp_data_fall[(temp_data_fall.loc[ : , i] * (1+alpha)) < temp_data_fall.loc[ : , j]]
        temp_data_rise = temp_data_rise[temp_data_rise.loc[ : , i] > (temp_data_rise.loc[ : , j] * (1+alpha))]

    select_data_fall = temp_data_fall
    # print(select_data_fall)
    wide_col_names = list(select_data_fall.columns)
    wide_col_names = wide_col_names[1:]
    wide_to_long_cols = wide_col_names[wide_col_names.index("AV Sector")+1:]
    select_data_fall_long = gather(select_data_fall, 'Year', select_fall_metric, wide_to_long_cols)
    # print(select_data_fall_long)
    source_fall.data = {
        'company_name': select_data_fall_long["Company Name"],
        'ticker': select_data_fall_long["Exchange:Ticker"],
        'country': select_data_fall_long["Country"],
        'region': select_data_fall_long["Region"],
        'sector': select_data_fall_long["AV Sector"],
        'year': select_data_fall_long["Year"],
        'metric': select_data_fall_long[select_fall_metric],
    }

    select_data_rise = temp_data_rise
    # print(select_data_rise)
    wide_col_names = list(select_data_rise.columns)
    wide_col_names = wide_col_names[1:]
    wide_to_long_cols = wide_col_names[wide_col_names.index("AV Sector")+1:]
    select_data_rise_long = gather(select_data_rise, 'Year', select_rise_metric, wide_to_long_cols)
    # print(select_data_rise_long)
    source_rise.data = {
        'company_name': select_data_rise_long["Company Name"],
        'ticker': select_data_rise_long["Exchange:Ticker"],
        'country': select_data_rise_long["Country"],
        'region': select_data_rise_long["Region"],
        'sector': select_data_rise_long["AV Sector"],
        'year': select_data_rise_long["Year"],
        'metric': select_data_rise_long[select_rise_metric],
    }

    return [select_data_fall, select_data_rise]

def update(attr, old, new):
    select_tables.children[1] = load_selection()
    select_tables.children[3] = load_selection()


#Widgets for update button
select_df_fall = Button(label="Load Falling Metrics Companies", button_type="primary")
select_df_fall.on_click(update)

select_df_rise = Button(label="Load Rising Metrics Companies", button_type="primary")
select_df_rise.on_click(update)

#Widgets for data fall table

columns_fall = [
    TableColumn(field="company_name", title="Company Name"),
    TableColumn(field="year", title="Year", width=100),
    TableColumn(field="sector", title="Sector", width=100),
    TableColumn(field="metric", title="Metrics", formatter=NumberFormatter(format="0,0.000"), width=100)
]

data_table_fall = DataTable(source=source_fall, columns=columns_fall, width=800, editable=True, fit_columns=True)

#Widgets for data rise table

columns_rise = [
    TableColumn(field="company_name", title="Company Name"),
    TableColumn(field="year", title="Year", width=100),
    TableColumn(field="sector", title="Sector", width=100),
    TableColumn(field="metric", title="Metrics", formatter=NumberFormatter(format="0,0.000"), width=100)
]

data_table_rise = DataTable(source=source_rise, columns=columns_rise, width=800, editable=True, fit_columns=True)


#Widgets for fall table selection
select_fall_table = Select(value=list(fall_db_wide.keys())[0],options=list(fall_db_wide.keys()))
select_fall_table.on_change("value",update)

#Widgets for rise table selection
select_rise_table = Select(value=list(rise_db_wide.keys())[0],options=list(rise_db_wide.keys()))
select_rise_table.on_change("value",update)


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

#Widgets for Slider
slider = Slider(start=-1.5, end=1.5, step=0.05, value=0, title="Metrics Change Level")
slider.on_change("value", update)

# full_year_list = list(sorted(set(fall_db_long[fall_table_keys[0]]["Year"])))
full_year_list = ['FY1998', 'FY1999', 'FY2000', 'FY2001', 'FY2002', 'FY2003',
 'FY2004', 'FY2005', 'FY2006', 'FY2007', 'FY2008', 'FY2009', 'FY2010', 'FY2011',
 'FY2012', 'FY2013', 'FY2014', 'FY2015', 'FY2016', 'IQ_LTM']
#Chose years
#Widgets for year selection
#Widgets for sector selection
def update_year_selection(attr, old, new):
    global year_name
    year_name = select_year.value

select_year = MultiSelect(value=["FY2014", "FY2015"], options=full_year_list, size=8)
select_year.on_change("value", update)
year_name = select_year.value

inspection_years = select_year.value
year_len = len(inspection_years)
first_inspect_year_index = full_year_list.index(inspection_years[0])
inspection_year_previous = full_year_list[first_inspect_year_index-1:first_inspect_year_index+year_len-1]
display_columns = info_list + inspection_years

def go_back():
    webbrowser.open_new_tab("http://162.243.172.69:5006/idea_generation_data")

goback_db = Button(label="Go Back", button_type="danger")
goback_db.on_click(go_back)


#Display widgets
select_tables = column(select_fall_table, data_table_fall, select_rise_table, data_table_rise)
main_select = column(select_year, select_region, select_country, select_sector, slider, goback_db)
# main_display = row(data_table_fall, data_table_rise)
lay_out = row(main_select, select_tables)
# lay_out = column(lay_out, f)
# lay_out = layout([[select_fall_table],[select_region],[select_country],[select_sector],[select_df_fall], [msg_title], [msg_info]])
curdoc().add_root(lay_out)

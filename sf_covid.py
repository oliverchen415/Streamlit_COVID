import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pendulum as pnd
import pydeck as pdk
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

today = pnd.now(tz='US/Pacific').format('MMMM DD, YYYY')
yest = pnd.yesterday().format('MMMM DD, YYYY')

st.title(f"COVID-19 Dashboard")
st.header(f'SF Cumulative Cases As of {today}')
env_key = 'API_KEY'

# DATA_URL = ('https://data.sfgov.org/resource/favi-qct6.csv?$$app_token=lolnope')
# DATE_COLUMN = 'data_as_of'

# st.markdown('Data sourced from '
            # '[data.sfgov.org](https://data.sfgov.org/COVID-19/Rate-of-COVID-19-Cases-by-Census-ZIP-Code-Tabulati/favi-qct6)')


DATA_URL = (f'https://data.sfgov.org/resource/tpyr-dvnc.csv?$$app_token={os.getenv(env_key)}')
DATE_COLUMN = 'last_updated_at'
st.markdown('Data sourced from '
            '[data.sfgov.org](https://data.sfgov.org/COVID-19/COVID-19-Cases-and-Deaths-Summarized-by-Geography/tpyr-dvnc)')

@st.cache
def load_data(nrows):
    # Caches the data
    # Cleans up the dates and ZIP codes
    data = pd.read_csv(DATA_URL, nrows=nrows, date_parser=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    data = data[data['area_type']=='ZCTA']
    data = data.drop(['area_type', 'multipolygon', 'deaths'], axis=1).rename(columns={'id': 'zip_code'})
    data = data.reset_index(drop=True)
    return data

data = load_data(264)

# My latitude and longitude information for each ZIP code that has data in SF data csv
map_zip_code = pd.DataFrame({
    'ZIPCode': [
        '94129','94123','94109','94133','94130',
        '94121','94118','94115','94108','94105',
        '94102','94122','94117','94103','94107',
        '94158','94114','94110','94127','94131',
        '94132','94112','94134','94124','94116',
        '94111','94104'
        ],
    'lat': [
        37.7973,37.7997,37.7935,37.8004,37.821,
        37.7766,37.7818,37.7852,37.7916,37.789,
        37.7789,37.7596,37.7701,37.7721,37.7805,
        37.7711,37.761,37.7594,37.7373,37.742,
        37.7213,37.721,37.7207,37.7344,37.7449,
        37.7966,37.7921
        ],
    'lon': [
        -122.465,-122.438,-122.42,-122.411,-122.37,
        -122.494,-122.456,-122.439,-122.408,-122.396,
        -122.42,-122.487,-122.448,-122.411,-122.395,
        -122.392,-122.436,-122.418,-122.459,-122.436,
        -122.484,-122.441,-122.413,-122.389,-122.485,
        -122.4,-122.402
    ],})

zip_data = pd.DataFrame({
    'ZIPCode': data['zip_code'],
    'CaseCount': data['count'],
})
zip_data.sort_values(by=['CaseCount'])
zip_data = zip_data.dropna(subset=['CaseCount'])

zip_rate = pd.DataFrame({
    'Rate': data['rate'],
    'ZIPCode': data['zip_code'],
})
zip_rate['Rate'] = zip_rate.round({'Rate':1})

map_zip_count = zip_data[zip_data.loc[:,'ZIPCode'].isin(map_zip_code['ZIPCode'])]
map_zip_count = map_zip_count.dropna()

map_zip_rate = zip_rate[zip_rate.loc[:,'ZIPCode'].isin(map_zip_code['ZIPCode'])]
map_zip_rate = map_zip_rate.dropna()

zip_map_data = pd.merge(map_zip_code,map_zip_count, on='ZIPCode')
zip_rate_data = pd.merge(map_zip_code, map_zip_rate, on='ZIPCode')
zip_rate_data = zip_rate_data.sort_values(by=['ZIPCode'])
zip_rate_data = zip_rate_data.reset_index(drop=True).sort_values(by='ZIPCode')
zip_rate_dict = zip_rate_data.loc[:,'ZIPCode'].to_dict()


if st.sidebar.checkbox('Show raw SF data'):
    st.subheader('Raw SF data')
    data = data.rename(columns={
        'zip_code': 'ZIP Code',
        'count': 'Case Count',
        'rate': 'Cases per 10,000 People',
        'acs_population': 'Population',
        'last_updated_at': 'Last Updated On'
    })
    data = data.sort_values(by=['ZIP Code'])
    data = data.dropna(subset=['Case Count']).reset_index(drop=True)
    st.write(data)
    data['Last Updated On'] = pd.to_datetime(data['Last Updated On'])
    date_updated = data['Last Updated On'][0].to_pydatetime().date()
    date_updated = date_updated.strftime('%B %d, %Y')
    st.info(f'Click on a column name to sort. Last updated {date_updated}. '
                'Case counts with no values have been dropped.'
                )

st.subheader('Number of Confirmed SF Cases by ZIP Code')

c = alt.Chart(zip_data).mark_bar().encode(
    y = alt.Y('ZIPCode:N',
                sort=alt.EncodingSortField(field='CaseCount', op='max', order='descending'),
                axis=alt.Axis(title='ZIP Code')),
    x = alt.X('CaseCount', axis=alt.Axis(title='Case Count')),
    tooltip = ['ZIPCode', 'CaseCount']
)

chart_text = c.mark_text(
    align = 'left',
    baseline = 'middle',
    dx = 3
).encode(
    text = 'Case Count'
)

(c+chart_text).properties(height=900)
st.altair_chart(c,use_container_width=True)

st.info('Mouse over a bar to see the number of cases. '
        'To expand the graph, click the toggle on the side of the graph. '
        'If your ZIP Code is not shown, fewer than 15 cases have been recorded there.'
)

st.markdown('---')

find_zip = st.selectbox('Select your ZIP Code.',
                        zip_rate_data.loc[:,'ZIPCode'])

case_num = 0
for i, zcode in zip_rate_dict.items():
    if zcode == find_zip:
        case_num = i

st.write('For ', find_zip, ', the number of cases per 10k people is',
        str(zip_rate_data.loc[case_num, 'Rate']), '.')

# Map

st.subheader('Map of COVID-19 Cases by ZIP Code')

st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/dark-v9',
     initial_view_state=pdk.ViewState(
         latitude=37.76,
         longitude=-122.4,
         zoom=11,
     ),
     layers=[
        pdk.Layer(
            "ScatterplotLayer",
            zip_rate_data,
            pickable=True,
            opacity=0.1,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position="[lon, lat]",
            get_radius="Rate*5",
            get_fill_color=[255, 140, 0],
            get_line_color=[0, 0, 0],
        ),
        pdk.Layer(
            'ScatterplotLayer',
            zip_rate_data[zip_rate_data['ZIPCode']==find_zip],
            pickable=True,
            opacity=0.2,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position="[lon, lat]",
            get_radius="Rate*5",
            get_fill_color=[0, 0, 255],
            get_line_color=[0, 0, 0],
        )

     ],
     tooltip={
        'html': 'Number of Cases per 10000 Residents in {ZIPCode}: <br>{Rate}</br>',
     },
 ))
st.info('Mouse over a circle to see the number of cases per 10,000 people. '
        'Click the toggle on the side to expand the map. '
        )



# California Data

# Old url for reference
# CA_DATA_URL = 'https://data.chhs.ca.gov/dataset/6882c390-b2d7-4b9a-aefa-2068cee63e47/resource/6cd8d424-dfaa-4bdd-9410-a3d656e1176e/download/covid19data.csv'
CA_DATA_URL = 'https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/926fd08f-cc91-4828-af38-bd45de97f8c3/download/statewide_cases.csv'
CA_DATE_COL = 'date'

@st.cache
def load_ca_data():
    ca_data = pd.read_csv(CA_DATA_URL)
    ca_data.loc[:, CA_DATE_COL] = ca_data.loc[:, CA_DATE_COL].map(pd.to_datetime)
    return ca_data

ca_data = load_ca_data()
ca_data = ca_data.rename(columns={
    'county': 'COUNTY',
    'totalcountconfirmed': 'TOTAL COUNT CONFIRMED',
    'totalcountdeaths': 'TOTAL COUNT DEATHS',
    'newcountconfirmed': 'NEW COUNT CONFIRMED',
    'newcountdeaths': 'NEW COUNT DEATHS',
    'date': 'DATE'
    })

recent_date = ca_data.loc[:, 'DATE'].max().date().strftime('%B %d, %Y')
first_date = ca_data.loc[:, 'DATE'].min().date().strftime('%B %d, %Y')
ca_county_list = ca_data.loc[:,'COUNTY'].unique()
ca_county_list = np.sort(ca_county_list).tolist()
ca_data_columns = [col for col in list(ca_data.columns) if col not in ['COUNTY', 'DATE']]

st.markdown('---')

column_names = ['TOTAL COUNT CONFIRMED', 'TOTAL COUNT DEATHS', 'NEW COUNT CONFIRMED', 'NEW COUNT DEATHS']
yest_data = ca_data[ca_data.loc[:, 'DATE'].dt.floor('d') == pnd.yesterday().to_formatted_date_string()].copy()

def max_in_county(column):
    column_max = ca_data.loc[:, column].idxmax()
    if column == 'TOTAL COUNT CONFIRMED':
            return (f'{ca_data.iloc[column_max]["COUNTY"]} has a total of '
                    f'{int(ca_data.iloc[column_max][column])} cases '
                    f'({round(ca_data.iloc[column_max][column]/yest_data.loc[:, column].sum(), 2)*100}% '
                    f'of all cases in CA) '
                    f'and {int(ca_data.iloc[column_max]["NEW COUNT CONFIRMED"])} new cases.'
                    )
    elif column == 'TOTAL COUNT DEATHS':
            return (f'{ca_data.iloc[column_max]["COUNTY"]} has a total of '
                    f'{int(ca_data.iloc[column_max][column])} deaths '
                    f'({round(ca_data.iloc[column_max][column]/yest_data.loc[:, column].sum(), 2)*100}% '
                    f'of all deaths in CA) '
                    f'and {int(ca_data.iloc[column_max]["NEW COUNT DEATHS"])} new deaths.'
                    )

st.markdown(f'**Quick CA Stats as of {pnd.yesterday().to_formatted_date_string()}**:')
st.write(f'The worst hit county is {ca_data.iloc[ca_data.loc[:, "TOTAL COUNT CONFIRMED"].idxmax()]["COUNTY"]}.')
for columns in column_names[0:2]:
    st.write(max_in_county(columns))

def max_in_state(colnames):
    if colnames == 'TOTAL COUNT CONFIRMED':
        return (f'California has a total of {int(yest_data.loc[:, "TOTAL COUNT CONFIRMED"].sum())} cases '
                f'and {int(yest_data.loc[:, "NEW COUNT CONFIRMED"].sum())} new cases.'
                )
    elif colnames == 'TOTAL COUNT DEATHS':
        return (f'California has a total of {int(yest_data.loc[:, "TOTAL COUNT DEATHS"].sum())} deaths '
                f'and {int(yest_data.loc[:, "NEW COUNT DEATHS"].sum())} new deaths.'
                )

for columns in column_names[0:2]:
    st.write(max_in_state(columns))

st.markdown('---')

if st.checkbox('Examine other counties in California?'):
    if st.sidebar.checkbox('Show raw CA data'):
        st.subheader('CA Raw COVID 19 Data')
        st.write(ca_data)
        st.info('Click on a column to sort. '
                'Click the toggle on the right side of the table to expand it.')
        st.warning("Unsure why the NEW COUNT columns go into the negatives, "
                   "since the total accumlation of deaths and confirmed cases "
                   "during the pandemic can't change."
                   )

    st.header('California COVID-19 Data')
    st.markdown('Data sourced from '
                '[data.ca.gov](https://data.ca.gov/dataset/covid-19-cases/resource/926fd08f-cc91-4828-af38-bd45de97f8c3)')
#                 '[data.ca.gov](https://data.ca.gov/dataset/california-covid-19-hospital-data-and-case-statistics/resource/5342afa3-0e58-40c0-ba2b-9206c3c5b288)')


    county = st.multiselect('Pick one or more counties to look at:',
                          ca_county_list,
                          ['San Francisco', 'Sacramento', 'Santa Clara']
                          )
    ca_columns = st.selectbox('Select a column to graph.',
                                ca_data_columns)
    ca_subset_columns = ca_data.loc[ca_data['COUNTY'].isin(county)].copy()
    ca_subset_columns.loc[:, 'DATE'] = ca_subset_columns.loc[:, 'DATE'].map(pd.to_datetime)
    ca_graph_columns = ca_subset_columns.loc[:,('COUNTY', 'DATE', ca_columns)].copy()

    county_chart = alt.Chart(ca_graph_columns).mark_line(size=4).encode(
        x='DATE',
        y = ca_columns,
        color = alt.Color('COUNTY', legend=alt.Legend(labelFontSize=15)),
        tooltip = ['COUNTY', 'DATE', ca_columns],
    )
    st.altair_chart(county_chart, use_container_width=True)
    st.info('Mouse over the line to see the exact count. '
            f'Data last updated on {recent_date}. '
            f'Data first captured on {first_date}.')

    st.markdown('---')

st.sidebar.markdown('Made by Oliver Chen. '
                    'Github repository available [here](https://github.com/oliverchen415/Streamlit_COVID).')

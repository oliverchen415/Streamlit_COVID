import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import pendulum as pnd
import pydeck as pdk

today = pnd.now(tz='US/Pacific').format('MMMM DD, YYYY')
yest = pnd.yesterday().format('MMMM DD, YYYY')

st.title(f"SF COVID Cases by Census ZIP Code")
st.header(f'As of {today}')

# DATA_URL = ('https://data.sfgov.org/resource/favi-qct6.csv?$$app_token=yh5qaeaJSvJrdOSv77ZnroO2u')
# DATE_COLUMN = 'data_as_of'

DATA_URL = ('https://data.sfgov.org/resource/tpyr-dvnc.csv?$$app_token=yh5qaeaJSvJrdOSv77ZnroO2u')
DATE_COLUMN = 'last_updated_at'

# st.markdown('Data sourced from '
            # '[data.sfgov.org](https://data.sfgov.org/COVID-19/Rate-of-COVID-19-Cases-by-Census-ZIP-Code-Tabulati/favi-qct6)')

st.markdown('Data sourced from '
            '[data.sfgov.org](https://data.sfgov.org/COVID-19/COVID-19-Cases-and-Deaths-Summarized-by-Geography/tpyr-dvnc)'
)

@st.cache
# def load_data(nrows):
#     # Caches the data
#     # Cleans up the dates and ZIP codes
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     data['zip_code'] = data['zip_code'].astype(str)
#     return data
def load_data(nrows):
    # Caches the data
    # Cleans up the dates and ZIP codes
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    data = data[data['area_type']=='ZCTA']
    data = data.drop(['area_type', 'multipolygon'], axis=1).rename(columns={'id': 'zip_code'})
    data = data.reset_index().drop('index', axis=1)
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
zip_rate_data = zip_rate_data.reset_index(drop=True)
zip_rate_dict = zip_rate_data.loc[:,'ZIPCode'].to_dict()



st.sidebar.info('**Info:** If you don\'t see data for your ZIP Code, '
        'there are 10 or fewer cases counted for your ZIP Code.'
        )
st.sidebar.warning('**Show Raw Data**: '
                    'Due to caching, the raw data may not display correctly. '
                    'The charts and map should be using the data last published '
                    'by the SF or CA government data portals.'
)

if st.sidebar.checkbox('Show raw SF data'):
    st.subheader('Raw SF data')
    st.table(data)
    date_updated = data[DATE_COLUMN][0].to_pydatetime().date()
    date_updated = date_updated.strftime('%B %d, %Y')
    st.info(f'Click on a column name to sort. Last updated {date_updated}')

st.subheader('Number of Confirmed SF Cases by ZIP Code')

c = alt.Chart(zip_data).mark_bar().encode(
    y = alt.Y('ZIPCode:N', sort=alt.EncodingSortField(field='CaseCount', op='max', order='descending')),
    x = 'CaseCount',
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
        'To expand the graph, click the fullscreen button on the side of the graph.'
)

st.subheader('Map of COVID-19 Cases by ZIP Code')

st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/dark-v9',
     initial_view_state=pdk.ViewState(
         latitude=37.76,
         longitude=-122.4,
         zoom=11,
     ),
     layers=[pdk.Layer(
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
     ],
     tooltip={
        'html': 'Number of Cases per 10000 Residents in {ZIPCode}: <br>{Rate}</br>',
     },
 ))
st.info('Mouse over a circle to see the number of cases per 10,000 people.')

find_zip = st.selectbox('Select your ZIP Code.',
                        zip_rate_data.loc[:,'ZIPCode'])

case_num = 0
for i, zcode in zip_rate_dict.items():
    if zcode == find_zip:
        case_num = i

st.write('For ', find_zip, ', the number of cases per 10k people is',
        str(zip_rate_data.loc[case_num, 'Rate']), '.')


CA_DATA_URL = 'https://data.chhs.ca.gov/dataset/6882c390-b2d7-4b9a-aefa-2068cee63e47/resource/6cd8d424-dfaa-4bdd-9410-a3d656e1176e/download/covid19data.csv'
CA_DATE_COL = 'Most Recent Date'

@st.cache
def load_ca_data():
    ca_data = pd.read_csv(CA_DATA_URL)
    #lowercase = lambda x: str(x).lower()
    #data.rename(lowercase, axis='columns', inplace=True)
    ca_data.loc[:, CA_DATE_COL] = ca_data.loc[:, CA_DATE_COL].map(pd.to_datetime)
    # ca_data.loc[:, CA_DATE_COL] = pd.to_datetime(ca_data.loc[:, 'Most Recent Date'])
    return ca_data

ca_data = load_ca_data()
# ca_data.loc[:, 'Most Recent Date'] = pd.to_datetime(ca_data.loc[:, 'Most Recent Date'])
recent_date = ca_data.loc[:, 'Most Recent Date'].max().date().strftime('%B %d, %Y')
ca_county_list = ca_data.loc[:,'County Name'].unique()
ca_county_list = np.sort(ca_county_list)
ca_data_columns = [col for col in list(ca_data.columns) if col not in ['County Name', 'Most Recent Date']]


st.markdown('---')

if st.checkbox('Examine other counties in California?'):
    if st.sidebar.checkbox('Show raw CA data'):
        st.subheader('CA Raw COVID 19 Data')
        st.write(ca_data)
        st.write('Click on a column to sort.')

    st.subheader('California COVID-19 Data')
    st.markdown('Data sourced from '
                '[data.ca.gov](https://data.ca.gov/dataset/california-covid-19-hospital-data-and-case-statistics/resource/5342afa3-0e58-40c0-ba2b-9206c3c5b288)')
    county = st.selectbox('Pick a county to look at:',
                          ca_county_list
    )
    ca_columns = st.selectbox('Select a column to graph.', ca_data_columns)
    ca_subset_columns = ca_data.loc[ca_data['County Name'] == county]
    ca_subset_columns.loc[:, 'Most Recent Date'] = ca_subset_columns.loc[:, 'Most Recent Date'].map(pd.to_datetime)
    ca_graph_columns = ca_subset_columns.loc[:,('Most Recent Date', ca_columns)]



    county_chart = alt.Chart(ca_graph_columns).mark_circle(size=60).encode(
        x='Most Recent Date',
        y = ca_columns,
        tooltip = ['Most Recent Date', ca_columns],
    ).interactive()
    st.altair_chart(county_chart, use_container_width=True)
    st.info(f'Mouse over a point to see the exact count. Data last updated on {recent_date}.')

    st.markdown('---')

    if st.sidebar.checkbox('Show subsetted CA data'):
        st.write(ca_subset_columns)



st.sidebar.markdown('Made by Oliver Chen. '
                    'Github repository available [here](https://github.com/boblandsky/Streamlit_tutorial).')
import streamlit as st
import numpy as np
import pandas as pd

"""
# My first app
Here's our first attempt at using data to create a table:
"""

df = pd.DataFrame({
    'first column': [1,2,3,4],
    'second column': [10,20,30,40]
})

df

if st.checkbox('Show Dataframe'):
    chart_data = pd.DataFrame(
        np.random.randn(20,3),
        columns=['a', 'b', 'c']
    )

st.line_chart(chart_data)

option = st.sidebar.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', option

map_data = pd.DataFrame(
    np.random.randn(1000,2)/[50,50] + [37.76, -122.4],
    columns=['lat', 'lon']
)

st.map(map_data)

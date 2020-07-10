# Streamlit Dashboard: COVID-19 Data for San Francisco and other California Counties

---
## Link
[COVID-19 Dashboard](https://sfcovid19dash.herokuapp.com/)

---

## Overview
* Created a web dashboard using Streamlit to visualize COVID-19 cases in San Francisco based on ZIP code, as well as cases in other California counties
* Data accessed from [Data SF](datasf.org) and [CA Data](data.ca.gov)
* Data processed and visualized using Pandas, Altair, Pydeck
* Deployed the Streamlit app on Heroku

---
## Goal
I wanted to put to use what I've learned about libraries such as Pandas and Altair. I found Streamlit, a way to make dashboards in Python and since we're in the middle of a pandemic (as of writing this), I wanted to apply it to making a dashboard for visualizing information on COVID-19.

---


## Screencap
![Image of app](https://github.com/boblandsky/Streamlit_COVID/blob/master/Annotation%202020-05-29%20120505.jpg)

---

![CA data](https://github.com/boblandsky/Streamlit_COVID/blob/master/Annotation%202020-06-26%20145950.jpg)

### Current features in the dashboard:
* Confirmed number of cases by ZIP Code
* Map of SF confirmed cases by ZIP Code
* Access additional information for other California counties
  * View information like Total Count Confirmed, Total Count Deaths, etc.
  * View changes over time

### Current issue(s):
* ~~Raw data does not load correctly, although the graphs and map appear to use correct data.~~ It doesn't appear to have anymore issues with loading older data. 
* Datasets can and have changed, I will need to monitor both app and data sources to make sure it stays up to date.

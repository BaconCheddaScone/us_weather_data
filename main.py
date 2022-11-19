import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import base64


# https://www.ncei.noaa.gov/access/search/data-search/daily-summaries
# https://www.ncdc.noaa.gov/cdo-web/datatools/findstation


#--------------------------- PAGE SET UP ---------------------------
## Page expands to full width
st.set_page_config(layout="wide")



#--------------------------- FETCH DATA THROUGH API ---------------------------
#USC00111550

def get_data(station):
    ENDPOINT = "https://www.ncei.noaa.gov/access/services/data/v1"
    PARAM = {
        "dataset": "daily-summaries",
        "stations": [f"{station}"],
        "startDate": "2015-01-01",
        "endDate": "2022-10-31",
        "bbox": "-171.791110603, 18.91619, -66.96466, 71.3577635769",
        "format": "json",
        "includeAttributes": 0,
        "includeStationName": 1,
        "includeStationLocation": 1,
        "units": "standard"
    }
    # The parameters include all stations located in Chicago.
    # I'll take an average of that later after we create a Dataframe.

    response = requests.get(url=ENDPOINT, params=PARAM)
    response.raise_for_status()
    data = response.json()

    df_original = pd.DataFrame(data)
    print(df_original.head())
    print(df_original.columns)

    df_modified = df_original[["DATE", "STATION", "NAME", "TMAX","LONGITUDE","LATITUDE"]]
    df_modified["TMAX"] = pd.to_numeric(df_modified["TMAX"])
    df_modified["DATE"] = pd.to_datetime(df_modified["DATE"])
    df_modified.rename(columns={"TMAX": "MAX_TEMP_F"}, inplace=True)

    # Take the avg of all Chicago stations to deem that the Max Temperature of that day.
    # df_final = df_modified.groupby(["DATE"], as_index=0).agg({"MAX_TEMP_F": "mean"})

    # we're entering ONE STATION so no need for group by
    df_final = df_modified
    # Insert new columns you may find useful - might not be necessarsy
    df_final.insert(loc=1, column="YEAR", value=df_final["DATE"].dt.year)
    df_final.insert(loc=2, column="MONTH", value=df_final["DATE"].dt.month)
    df_final.insert(loc=3, column="DAY", value=df_final["DATE"].dt.day)

    print(df_final.columns)


    return df_final


#--------------------------- FILE DOWNLOAD ---------------------------

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="weather.csv">Download CSV File</a>'
    return href


#--------------------------- SIDEBAR ---------------------------


selection_station = st.sidebar.text_input("Enter a Weather Station ID","USC00111550")
selection_year = st.sidebar.multiselect(label="Select desired year(s)",options=list(reversed(range(2015,2023))), default=[2022])
selection_month = st.sidebar.selectbox("Select a month",list(range(1,13)))

if selection_station and selection_year:
    df = get_data(selection_station)
    print(df.head())

#--------------------------- SET UP MAIN DASHBOARD ---------------------------

st.title("Weather We Come")
st.header("""See how hot each day has been and compare across the years""")
st.markdown("""Data is available thanks to the **National Centers for Environmental Information**, 
a division of the National Oceanic and Atmospheric Administration""")

st.header("How to use this tool")
st.markdown("""
- Use the sidebar (on mobile, click the arrow on the top left-hand corner) \n
- Find a station id [here](https://www.ncdc.noaa.gov/cdo-web/datatools/findstation) \n
- Select at least one year.\n
- Select a month.\n
- Select multiple years to conduct a year-over-year analysis.\n
""")

#--------------------------- SET UP CHART AREA---------------------------

# Create new DF filtered for the selections made in to-do-1
df_filtered = df.loc[(df["YEAR"].isin(selection_year))
                           & (df["MONTH"] == selection_month)]


# Bring in city name of Station.
city_name = str(df_filtered.NAME.unique())

#remove the [' '] around the NAME.
for char in city_name:
    if char in "[']":
        city_name = city_name.replace(char, "")


st.header("Weather Chart")
st.write("Displaying data for " + city_name)
chart = px.line(
    x=df_filtered["DATE"].dt.day,
    y=df_filtered["MAX_TEMP_F"],
    color=df_filtered["DATE"].dt.year,
    hover_name=df_filtered["DATE"].dt.date,
    markers=True,
    labels={
        "x": "Day of Month",
        "y": "Daily Temperature High (Fahrenheit)",
        "color": "Year"
    }
)
st.plotly_chart(chart)
st.markdown(filedownload(df_filtered), unsafe_allow_html=True)













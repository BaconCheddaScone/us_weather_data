import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import base64
import sqlite3
from sqlite3 import Error




#--------------------------- PAGE SET UP ---------------------------
## Page expands to full width
st.set_page_config(layout="wide")


#--------------------- SQL CONNECTION SET UP ---------------------#
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB succesful")
    except Error as e:
        print(f"The error {e} occurred")

    return connection

#--------------------- SQL SELECT RECORDS ---------------------#

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"An error {e} occurred while attempting to fetch data.")



#--------------------------- FETCH DATA THROUGH NCEI API ---------------------------
# Example station ID: USC00111550

@st.cache
def get_data(station):
    # remove the "GHCND:" at the front of valid station name

    ENDPOINT = "https://www.ncei.noaa.gov/access/services/data/v1"
    PARAM = {
        "dataset": "daily-summaries",
        "stations": [f"{station}"], #this is the station ID
        "startDate": "2015-01-01",
        "endDate": "2022-10-31",
        "bbox": "-171.791110603, 18.91619, -66.96466, 71.3577635769",
        "format": "json",
        "includeAttributes": 0,
        "includeStationName": 1,
        "includeStationLocation": 1,
        "units": "standard"
    }

    response = requests.get(url=ENDPOINT, params=PARAM)
    response.raise_for_status()
    data = response.json()

    df_original = pd.DataFrame(data)
    # print(df_original.head())
    # print(df_original.columns)

    df_modified = df_original[["DATE", "STATION", "NAME", "TMAX","LONGITUDE","LATITUDE"]]
    df_modified["TMAX"] = pd.to_numeric(df_modified["TMAX"])
    df_modified["DATE"] = pd.to_datetime(df_modified["DATE"])
    df_modified.rename(columns={"TMAX": "MAX_TEMP_F"}, inplace=True)

    df_final = df_modified
    # Insert new columns you may find useful - might not be necessarsy
    df_final.insert(loc=1, column="YEAR", value=df_final["DATE"].dt.year)
    df_final.insert(loc=2, column="MONTH", value=df_final["DATE"].dt.month)
    df_final.insert(loc=3, column="DAY", value=df_final["DATE"].dt.day)
    #
    # print(df_final.columns)


    return df_final


#--------------------------- FILE DOWNLOAD ---------------------------

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="weather.csv">Download CSV File</a>'
    return href


#--------------------------- SIDEBAR ADDITIONAL ---------------------------
# First, run the method to connnect to SQL db
connection = create_connection("ncei.db")

states_avail = reversed(["WI","WV","WA","VA","VT","UT","TX","TN","SD","SC","RI","PA","OR","OK","OH","ND","NC","NY","NM",
                         "NJ","NH","NV","NE","MT","MO","MS","MN","MI","MA","MD","ME","LA","KY","KS","IA","IN","IL","ID",
                         "HI","GA","FL","DE","CT","CO","CA","AR","AZ","AK","AL"])
# Next, grab user inputs from streamlit sidebar
user_input_state = st.sidebar.selectbox("Select a state", states_avail)
user_input_city = st.sidebar.text_input("Enter a city")

# This is the query I'd use in SQL to just fetch the data with filters from user input.
# I'm actually pulling from a View instead of a table.
select_query = f"SELECT * FROM 'USC_GHCND_summary_vw' " \
               f"WHERE station_name like '%{user_input_city}%' AND state = '{user_input_state}'"

# This runs the method to fetch all relevant data.

query_result = execute_read_query(connection, select_query)
# print(query_result)
# Example:  [('USC00110072', 'ALEDO', 'IL', 'TMAX', 1901, 2022),
# print(type(query_result))


dict = {}

if query_result != None:
    # st.sidebar.text("Select one station from below")
    # result_pd = pd.DataFrame(data=query_result, columns=db_columns)
    try:
        dict = [{"station_id":a[0],"station_name":a[1], "state":a[2], "element_type":a[3], "latitude":a[4],
                 "longitude":a[5],"begin_date":a[6],"end_date":a[7]} for a in query_result]
    except:
        print("I dunno man. I dunno")

    # Use this as a test to verify whether data is pulling in.
    # After it all appear to work, comment these out.
    result_db = pd.DataFrame(dict)
    st.sidebar.write("Here are all of the stations available in that area")
    st.sidebar.write(result_db[["station_name", "station_id"]])

    ### TESTING: COMMENT OUT THE FOLLOWING LINES ###
    # st.write("This confirms the type")
    # st.write({type(result_db)})
    #
    # st.write("This shows the top 5 results or less")
    # st.write(result_db.head())
    #
    # st.write("This shows the column names fetched from the SQL table holding station inventory")
    # st.write("If this shows up empty, it means there are no stations in " + user_input_city)
    # st.write(result_db.columns)
    # #
    # st.write("This shows the datatype of the latitude column. I need to make that a str in order to pass it into a map library")
    # st.write(type(result_db["latitude"]))
    #


else:
    st.sidebar.text("Sorry, please try again")


#---------------------------------------- MAP ATTEMPT 2 --------------------------------------#

# map = leafmap.Map(google_map="HYBRID")
# st.map(map)
# map.add_points_from_xy(data=result_db, x=longitude, y=latitude)
# map.to_streamlit(height=500)


#---------------------------------------- MAP ATTEMPT 1 --------------------------------------#
# From query_result, tap into the station name & lat/long.
# Turn that into a

# map_df = pd.DataFrame(
#     data = [[-89.24, 37.78]],
#     columns = ["longitude", "latitude"]
# )
#
# print(map_df)
# st.sidebar.map(map_df)




#--------------------------- SIDEBAR MAIN ---------------------------
# If going for drop-down method. 
# station_list = [item for item in result_db["station_name"]]
# selection_station_name = st.sidebar.selectbox("Select one Weather Station your area:", options=station_list)

selection_station_id = st.sidebar.text_input("Copy & paste desired Weather Station ID from above","USC00111550")

# selection_station_id = result_db["station_id"][result_db.station_name == selection_station_name][1]
# st.write(selection_station_id)


selection_year = st.sidebar.multiselect(label="Select desired year(s)",options=list(reversed(range(2015,2023))), default=[2022, 2021, 2020, 2019])
selection_month = st.sidebar.selectbox("Select a month",list(range(1,13)))

if selection_station_id and selection_year:
    df = get_data(selection_station_id)
    # print(df.head())



#--------------------------- SET UP MAIN DASHBOARD ---------------------------

st.title("Weather We Come")
st.header("""See how hot each day has been and compare across the years""")
st.markdown("""Data is available thanks to the **[National Centers for Environmental Information](https://www.ncei.noaa.gov/)**
a division of the National Oceanic and Atmospheric Administration""")


with st.expander("💡How to use this tool"):
    st.markdown("""
    - Use the sidebar (on mobile, click the arrow on the top left-hand corner) \n
    - Select a State and type in a city to find a list of participating station ID \n 
    - Copy/paste the station ID \n
    - Select at least one year.\n
    - Select a month.\n
    - Select multiple years to conduct a year-over-year analysis.\n
    - You can even download the raw data file as a .csv!
    """)

# st.expander(label=st.header("How to use this tool"))
# st.header("How to use this tool")



#--------------------------- SET UP CHART AREA---------------------------

# Create new DF filtered for the selections made
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













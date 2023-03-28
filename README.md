# About Weather We Come
This is a nifty web app that will help you
* See historic daily-max temperatures, and
* Compare those daily maxes across multiple years.

## The Origin Story
This initially started as a personal project to convince my condominium board members and neighbors to make changes to our building based on weather patterns. The idea was quite simple:
1. Prove with data that it's getting warmer, sooner in the year.
2. Do it without boring them - make it interactive. 

But then I thought, "why stop in one city? Why not scale it?" <br>
Thus, the app now pulls in data for the entire United States. 

## About The Data
It's suprisingly difficult to find historical weather data. Luckily, the **National Centers for Environmental Information (NCEI)**, a division of the National Oceanic and Atmospheric Administration 
has access to all sorts of weather and climate data.
The app is streaming data in through their API.

**More on the data source** <br>
Menne, M.J., I. Durre, B. Korzeniewski, S. McNeill, K. Thomas, X. Yin, S. Anthony, R. Ray, 
R.S. Vose, B.E.Gleason, and T.G. Houston, 2012: Global Historical Climatology Network - 
Daily (GHCN-Daily), Version 3. [indicate subset used following decimal, 
e.g. Version 3.12]. 
NOAA National Climatic Data Center. http://doi.org/10.7289/V5D21VHZ

**Mapping the meta data** <br>
The biggest challenged involved with this app wasn't making the API call.<br>
It was figuring out how to identify which weather station IDs had the appropriate data.<br> 
* Weather station ID is a required parameter for the API. <br>
* Not every weather station provides daily-level data. <br>
* Even among those that do, not all of will have max temperature data. <br>

So, how does one go about figuring out which weather station IDs are appropriate for the analysis? <br>
After much digging, I discovered NCEI's list of meta data of the Global Historical Climatology Network - Daily (GHCN-Daily) <br>
which is essentially the source of the data in question. The key ingredients were: <br>
* Stations: Weather stations by State, Station Name, and Station ID.<br>
* Inventory: Weather stations IDs, the meteorological elements they provide (such as daily max temperature), and year(s) data is available for.<br>

In the backend, I'm using SQLite/SQLAlchemy to <br>
1. Filter for just the Weather Station IDs that supply daily-level data for the United States.
2. Join #1 with the Inventory data to further isolate to stations that have Daily Max Temperature data, for 2015 and after.



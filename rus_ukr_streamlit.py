import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path
import datetime
import json
import datetime
import geopandas as gpd
import shapely
import geopy.distance
import os

st.set_page_config(layout="centered",page_title="Russia-Ukraine War Analysis")
st.title('Russia - Ukraine War EDA')
st.subheader('Identifying a shift in Russian battle style and its implications')

st.markdown('By: [Matthew Moellering](https://www.linkedin.com/in/matthew-moellering/) & [Karshni Mitra](https://www.linkedin.com/in/karshnimitra/)')

st.markdown("Watch our video [here](https://www.youtube.com/watch?v=nzEzbowGgRU).")

st.header('Motivation:')
st.markdown('''The Russia-Ukraine War has displaced over 14 million people and current estimates have the current death toll at least 200,000. The Russian invasion of Ukraine is one of the most horredous and evil acts we have seen this century.
 The Ukrainian people under the leadership of President Zalensky have fought honorably and have united the West and NATO around their cause. As winter ends, both sides are predicted to begin fresh offensives or counter-offensives. 
For Russia the goal is to take more land and place the Ukrainians in a position where they will sue for peace and cede control of the Donbas.
\nPreviously, a swift victory by Russia was predicted by basically everyone. Why? Offensive warfare has been supreme since the United States won the Gulf War using a strategy called Air Land Battle. 
This concept has dominated warfare since then and has been the golden standard, but does it still hold? Does the data from Ukraine back this?
\nIf this does not hold, we could possibly argue that offensive warfare should not be considered a viable strategy anymore, in spite of pre-war speculations and probabilities of swift 'victories'.
\nA promising finding would be a quantitative assessment that the offense-defense paradigm is shifting towards defense with the integration of new technologies on the battlefield. 
With quantified results, analysis like this could potentially deter future attacks as military powers may realise it may not be worth the 'cost'.
Currently, an actionable insight would be increasing awareness about the significance of defense so that the international community could increase its spending on Taiwanese defense, making them a porcupine that deters the Chinese Communist Party from starting a war. 
A strong defense may prevent war all together. Our primary objective is to prove that offensive war strategy is not worth the cost, be it military equipment, infrastructure damage or most importantly, human lives.
''')


with st.expander("Secondary Objectives and Possible Future Analysis"):
    st.header("Secondary Objectives")
    st.subheader("Tactical Analysis:")
    st.markdown('''A quantitative analysis could prove benifical for 
    Ukraine and its allies to decide what kind of military supplies to provide, what strategies to employ etc.
    It could give us better understanding if NATO equipment packages are significant and if NATO is sending the right equipment to the Ukranians to help them win the war?  
    \nFinally, can we quantify potential endings? Many experts are preditcing a slogging war of attrition, but Kremlin regime change, a Russian Army collapse, or Ukranian win are possible.''')

# ## Import Datasets

path = Path.cwd()

data_path = path.joinpath('Data')
russia_losses = data_path.joinpath('russia_losses_equipment.csv')
russia_losses_p = data_path.joinpath('russia_losses_personnel.csv')
battle_data = data_path.joinpath('acled_battle_data_23Feb.csv')

maps = data_path.joinpath("ukraine_geojson-master")
ukraine_map_path = maps.joinpath("UA_FULL_Ukraine.geojson")

df_equipment = pd.read_csv(russia_losses, sep=',')
df_personnel = pd.read_csv(russia_losses_p, sep=',')
df_battle = pd.read_csv(battle_data, sep=',')

st.header('Import and analyze the ACLED battle dataset')

st.dataframe(df_battle.head(5).T)

#Check stats for the dataset
st.markdown('Analyzing the statistics of the data')
st.dataframe(df_battle.describe().T,height=492)

#Convert event date to datetime
df_battle['event_date'] = pd.to_datetime(df_battle['event_date'])

#Checking number of entries by day to identify days with greatest activity
df_battle['event_date'].value_counts()

st.markdown("Identifying types of events in the data")
st.code('''#Types of events in the dataset
df_battle['event_type'].unique()''')

#Types of events in the dataset
st.dataframe(df_battle['event_type'].value_counts(),width=250)

#Create a subset of the dataset which includes only battles
df_battles_only = df_battle[df_battle["event_type"] == 'Battles'].copy()
print ("Number of battles:",len(df_battles_only))

#See the sub-event types for the battles dataset
df_battles_only['sub_event_type'].unique()	

#Convert event date to datetime
df_battle['event_date'] = pd.to_datetime(df_battle['event_date'])

#Get base Ukraine Map geojson
with open(ukraine_map_path, encoding="utf8") as f:
    ukraine_map = json.load(f)

# To identify if app is running on streamlit
def is_running_on_streamlit():
     return "HOSTNAME" in os.environ and os.environ['HOSTNAME'] == 'streamlit'

# Defining a function **get_base_Ukraine_map** that returns a map of Ukraine with states/regions outlined
def get_base_Ukraine_map(title="No Title"):
    '''
      Return a base map of Ukraine
      with the states outlined
      with title
    '''

    # Create the base map
    base = alt.Chart(alt.Data(values=ukraine_map)).mark_geoshape(
        stroke='black',
        strokeWidth=0.5
    ).encode(
      color=alt.value('#f5f5f5')
    ).project(
      type='mercator',
      scale=1100,
      center=[31, 49] 
  ).properties(
      width=770,
      height=500,
      title=title
  )

    return base



def get_Kyiv_point(size=100):
    # Create a DataFrame with the coordinates for Kyiv
    kyiv_df = pd.DataFrame({
        'latitude': [50.450001],
        'longitude': [30.523333],
        'city': ['Kyiv']
    })

    # Create the red dot for Kyiv
    kyiv = alt.Chart(kyiv_df).mark_circle(
        size=size,
        color='red'
    ).encode(
        longitude='longitude:Q',
        latitude='latitude:Q',
        tooltip='city:O'
    ).project(
        type='mercator',
        scale=1100,
        center=[31,49]
    )

    return kyiv

#Filter out events tagged as 'Strategic developements'
df_battle_subset = df_battle[df_battle['event_type'] != 'Strategic developments']

st.markdown("Filter out 'Strategic developments' for the upcoming visualizations")
st.code('''#Filter out events tagged as 'Strategic developements'
df_battle_subset = df_battle[df_battle['event_type'] != 'Strategic developments']''')


# A geographical area that represents Kyiv, the Ukraine capital
# In maps below, used to identify the amount of battles fought near the area
kyiv = get_Kyiv_point(500)

st.header("Visual Analysis")

st.subheader('Battles and explosions - first 40 days of the war')

#Setting the date range to plot
start_date = df_battle['event_date'].min()
end_date = pd.to_datetime('2022-3-31')

#Filtering the dataset based on the date range
df_battle_march2022 = df_battle_subset[(df_battle_subset['event_date'] > start_date )
                                       & (df_battle_subset['event_date'] < end_date)]

#Getting the base map
base = get_base_Ukraine_map("Events in first 40 days of the war")

#Marking all the events in the given date range
circle_points = alt.Chart(df_battle_march2022).mark_circle(
    opacity=0.8,
    stroke='black',
    strokeWidth=1,
).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['location:N','event_type:O'],
    color=alt.Color('event_type:O', scale=alt.Scale(scheme='dark2'))
).project(
    type='mercator',
    scale=1100,
    center=[31, 49]
)

combined = alt.layer(base,circle_points,kyiv).configure_legend(labelLimit=0)

st.altair_chart(combined, use_container_width=True)

st.markdown('**Figure 1**: The map above shows battles and remote explostions that occured in the first 40 days of the war (up till March 31, 2022). We can see that Russia primarily attacked on 2 fronts; the northern and eastern borders. The red circle shows Kyiv (the capital) and it can be observered that there are a lot of battles and explosions in this timeframe around Kyiv. The Russian offensive from the Northern front attempted to conquer Kyiv.')

st.subheader('Battles and explosions - December 1, 2022 to January 31, 2023')

#Setting the date range to plot
start_date = pd.to_datetime(datetime.date(2022,12,1))
end_date = df_battle['event_date'].max()

#Filtering the dataset based on the date range
df_battle_dec2022 = df_battle_subset[(df_battle_subset['event_date'] > start_date) 
                                     & (df_battle_subset['event_date'] < end_date)]

#Getting the base map
base = get_base_Ukraine_map("Events from 1st December 2022 to 15th January 2023")

#Marking all the events in the given date range
circle_points = alt.Chart(df_battle_dec2022).mark_circle(
    opacity=0.8,
    stroke='black',
    strokeWidth=1,
).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['location:N','event_type:O'],
    color=alt.Color('event_type:O', scale=alt.Scale(scheme='dark2'))
).project(
    type='mercator',
    scale=1100,
    center=[31, 49])

#Overlaying the different maps
map = base + kyiv + circle_points

#Remove map edge borders
map.configure_view(stroke=None).configure_legend(labelLimit=0)
st.altair_chart(map.configure_legend(labelLimit=0))

st.markdown('''**Figure 2**: The plot above shows the battles and explosions from December 1, 2022 to January 15, 2023. Ukraine was successful in pushing back the Russian offensives from the Northern border, as there are no battles being fought around the capital in this timeframe. Some remote explosions are still happening in and around the capital, but there is significantly less activity around the capital at this time.
It is also interesting to note that the Eastern front of the Russian offensive has also not been able to capture more land for over 8 months. Thus, Ukraine has been successful in pushing back Russia on the Northern front and holding the Russian offensives back on the Eastern front, making them resort more to remote warfare.''')



st.markdown('Since the Russian offensive failed and they were unable to capture a lot of land in Ukraine, they resorted to remote explosions that had nothing to do with attacks in battles. Primary targets may have been cities, civilian populations, infrastructure such as power grids, radio towers etc.')

# Value counts of event types
st.write(df_battle_subset['event_type'].value_counts())

st.markdown("Checking for erroneous entries")
st.code('''#Check whether 'data_id' is unique for every row and there is no faulty entry
df_battle_subset['data_id'].nunique() == len(df_battle_subset)''')

#Check whether 'data_id' is unique for every row and there is no faulty entry
df_battle_subset['data_id'].nunique() == len(df_battle_subset)


def calculate_update_civ_explosions():
    # Get all explosions in the data
    df_explosions = df_battle[df_battle['event_type']=='Explosions/Remote violence']

    civilian_explosion_ids = []

    # Iterate through every explosion
    for idx,explosion_row in df_explosions.iterrows():

        # Retrieve explosion location as a tuple
        explosion_loc = (explosion_row['latitude'],explosion_row['longitude'])

        # Define a flag variable
        battle_explosion = False

        # Identify the range of dates for that particular explosion
        start_date = explosion_row['event_date'] - pd.DateOffset(days = 21)
        end_date = explosion_row['event_date'] + pd.DateOffset(days = 10)

        # Identify all battles within the selected range
        df_battles_within_range = df_battles_only[(df_battles_only['event_date'] > start_date) 
                                                  & (df_battles_only['event_date'] < end_date)]

        # Iterate through every battle in the given timeframe
        for _,battle_row in df_battles_within_range.iterrows():

            # Retrieve battle location
            battle_loc = (battle_row['latitude'],battle_row['longitude'])
            
            # Compute distance between battle location and explosion
            if geopy.distance.geodesic(explosion_loc, battle_loc).km < 100:
                
                # If distance is less than 100km, mark as a battle explosion and break
                battle_explosion=True
                break

        # If it is not a battle explosion, append data_id to a list
        if not battle_explosion:
            civilian_explosion_ids.append(explosion_row['data_id'])


    # Filter out explosions based on data_id's tagged as non battle explosions
    civ_explosions = df_battle_subset[df_battle_subset['data_id'].isin(civilian_explosion_ids)].copy()

    # Save to csv
    civ_explosions.to_csv(r'./Data/civ_explosions.csv')

    # Return computed value
    return civ_explosions


@st.cache_data()
def get_civilian_explosions():
    civ_explosions=None
    if is_running_on_streamlit():
        try:
            civ_explosions=pd.read_csv(r'./Data/civ_explosions.csv')
        except:
            civ_explosions=calculate_update_civ_explosions()
    else:
        civ_explosions=calculate_update_civ_explosions()
    return civ_explosions

civ_explosions = get_civilian_explosions()

st.subheader("Plotting non-battle (remote) attacks")

st.write('Number of non battle explosions:', len(civ_explosions))

# Create a column 
civ_explosions['event_date'] = pd.to_datetime(civ_explosions['event_date'])
civ_explosions['year_month'] = civ_explosions['event_date'].map(lambda x : x.month_name() + ', '+ str(x.year))
civ_explosions.sort_values(by='event_date',inplace=True)

# Group remote explosions by month and year
grouped = civ_explosions.groupby(by=['year_month']).agg({'data_id':'count','event_date':'min'})[['data_id','event_date']]

# Reset index to get month as a column
grouped.reset_index(inplace=True)

# Create the base map (has different dimensions and centering from the one in get_base_Ukraine_Map())
base = alt.Chart(alt.Data(values=ukraine_map)).mark_geoshape(
      stroke='black',
      strokeWidth=0.5
  ).encode(
      color=alt.value('#f5f5f5'),
  ).project(
      type='mercator',
      scale=1100,
      center=[31, 55] 
  ).properties(
      width=500,
      height=400,
      title="Remote explosions by month"
  )

# Define the selector that enables chart interactivity
select_month = alt.selection_single(encodings=['x'])

# Get all points to plot
circle_points = alt.Chart(civ_explosions).mark_circle(
    opacity=0.8,
    stroke='black',
    strokeWidth=1,
).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['location:N','event_type:O'],
    color=alt.condition(select_month,
                        alt.Color('year_month:O', scale=alt.Scale(scheme='dark2'),sort=['event_date']),
                        alt.value('lightgray')),
    opacity = alt.condition(select_month, 
                            alt.value(1.0), 
                            alt.value(0))
).project(
    type='mercator',
    scale=1100,
    center=[31, 55])


# Create map with overlaying the points
map = alt.layer(base,circle_points,kyiv)

# Create the bar graph that shows counts of explosions by month
bar_slider = alt.Chart(grouped).mark_bar().encode(
    x={
        'field':'year_month',
       'sort':{'field':'event_date'},
       'title':'Month'
       },
    y={
        'field' :'data_id',
       'type':'quantitative',
       'title' : 'Explosion Count'
       },
    color=alt.condition(select_month,
                        alt.value('#1f77b4'),
                        alt.value('lightgray'))
).properties(height=100,width=500).add_selection(select_month)

st.altair_chart(alt.vconcat(map,bar_slider))

st.markdown('''**Figure 3:** The map above shows remote explosion points that have occurred outside a 100km radius of any battle in the last 21 days. 
Explosions have also been filtered out if a battle takes place within a 100 km radius in the *next* 10 days, 
since these are technically considered *preparatory attacks*. 
\nThe bar chart below shows the explosion counts by month.
This map is interactive. Clicking on the bar chart will highlight explosion points on the Ukraine map in that particular month.
\n
In the bar chart, it is evident that the number of remote explosions that are away from battles, significantly increase in the first few months of the war. 
We attribute this to the failure of the Russian offensive on both fronts. They had to resort to remote attacks in other parts of Ukraine, presumably targetting civilian areas and necessary infrastructure.''')

st.header('Analyzing the Line of Battle')
st.markdown('For further analysis, we started by plotting the points of all the battles during one (random) day of the war.') 

start_date = datetime.date(2022, 10, 15)
end_date = datetime.date(2022, 10, 15)
dates = [start_date + datetime.timedelta(days=x) for x in range(0, 1)]
df_battles_only['event_date'] = pd.to_datetime(df_battles_only['event_date'])

#create the dataframe
df_battle_subset_Nov1 = df_battles_only[df_battles_only['event_date'].isin(dates)]

# Create the base map
base = get_base_Ukraine_map("Battles on October 15th, 2022")

circle_points = alt.Chart(df_battle_subset_Nov1).mark_circle(
    opacity=0.8,
    stroke='black',
    strokeWidth=1,
).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['location:N','event_type:O'],
    color=alt.Color('sub_event_type:O', scale=alt.Scale(scheme='dark2'))
).project(
    type='mercator',
    scale=1100,
    center=[31, 49]
    ).properties(title='Battles on October 15th, 2022')
    
# Overlay the maps    
map = base + circle_points 

st.altair_chart((base + circle_points ).configure_legend(labelLimit=0))

st.markdown('''**Figure 4:** The figure above is a simple geospatial 
            representation of the locations where battles were fought on October 15th, 2022.
              A day with relatively less battles have been chosen to show how we have identified the line of battle.''')

st.subheader("Establishing the line of battle")

st.markdown("We then drew a line connecting all points on the battlefield.")

line = alt.Chart(df_battle_subset_Nov1).mark_line(
    opacity=0.8,
    stroke='red',
    strokeWidth=3,
).encode(
    order='latitude:O',
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['location:N','event_type:O'],
).project(
    type='mercator',
    scale=1100,
    center=[31, 49]
    ).properties(
    width=500,
    height=500,
    title='Battles on October 15th, 2022'
)

# Overlay the maps
map = base + circle_points + line

st.altair_chart(map.configure_legend(labelLimit=0))

st.markdown("**Figure 5:** The map above shows a line connecting all the battle points in Figure 4, to establish and visualize the line of battle on a particular day. In this case, October 15th 2022.")

st.subheader("Establishing the line of battle by month")

st.markdown('''Next, we aggregated the battles *by month*, and repeated the two steps above.
\n1) Plotted all the battles
2) Drew a line that connected all the battles\n''')

start_date = datetime.date(2022, 3, 7)
end_date = datetime.date(2023, 1, 7)

dates = [start_date + datetime.timedelta(days=x*30) for x in range(0, 11)]
df_battles_only['event_date'] = pd.to_datetime(df_battles_only['event_date'])

def create_line_list(battles_df, dates_list):
    '''
      This function takes in a dataframe and a list of dates
      and creates a list of altair lines that can demonstrate multiple avenues of attack.
      create_line_list(df0)-->  [line1, line2, line 3 ]
    '''

    df_battle_subset= df_battles_only[df_battles_only['event_date'].isin(dates)]
    pass

# create the dataframe
df_battle_subset_by_month = df_battles_only[df_battles_only['event_date'].isin(dates)].copy()

# Create a columm to read month easier
df_battle_subset_by_month['month_year'] = df_battle_subset_by_month['event_date'].map(
    lambda x : x.month_name() + ', ' + str(x.year))

# Create the base map
base = get_base_Ukraine_map("Battle Lines By Month")

# Mark all the battle points
circle_points = alt.Chart(df_battle_subset_by_month).mark_circle(
    opacity=1,
    stroke='black',
    strokeWidth=1,
).encode(
    latitude='latitude:Q',
    longitude='longitude:Q',
    tooltip=['location:N','sub_event_type:O', 'event_date:O'],
    color=alt.Color('sub_event_type:O', scale=alt.Scale(scheme='dark2'))
).project(
    type='mercator',
    scale=1100,
    center=[31, 49])

# Mark the line connecting all the points
line_total = alt.Chart(df_battle_subset_by_month).mark_line(
    opacity=0.6,
    strokeWidth=2,
).encode(
    order='latitude:O',
    latitude='latitude:Q',
    longitude='longitude:Q',
    color=alt.Color('month_year:O', scale=alt.Scale(scheme='goldred'),sort=['event_date'])
).project(
    type='mercator',
    scale=1100,
    center=[31, 49]
    ).properties(
    width=500,
    height=500,
    title='November 2022'
)

# Layer the maps and preserve their independent color schemes
map = alt.layer(base,circle_points,line_total).resolve_scale(color='independent')

# Remove map edge borders
map.configure_view(stroke=None)
map.configure_legend(labelLimit=0)
st.altair_chart(map)

st.markdown("**Figure 6:** The map above shows all the battle points and lines, plotted by month. The points are sub-categorized into Armed Clashes, Government (Ukraine) regains territory and Non - state (Russia) actor overtakes territory. All these events are connected monthwise by a line. This displays the line of battle by month.")

st.markdown("Clearly, we need to separate the two fronts of battle since the lines are 'zig-zagging' and join the points based on longitude for the Northern Front and latitude for the Eastern front.")

st.markdown('From online sources, we identify important battle locations on both fronts and retrieve their latitude and longitude from Google searches.')

st.code('''
    # East Battle Points 
    odessa = shapely.geometry.Point(46.47747, 30.73262) 
    sevastopol = shapely.geometry.Point(44.58883, 33.5224)
    kerch = shapely.geometry.Point(45.3607, 36.4706)
    mariupol = shapely.geometry.Point(47.09514, 37.54131) 
    luhansk = shapely.geometry.Point(48.56705, 39.31706) 
    vovchansk = shapely.geometry.Point(50.29078, 36.94108)
    \n
    # North Battle Points
    dobryanka = shapely.geometry.Point(52.0601, 31.1837)
    seredyna = shapely.geometry.Point(52.1837, 34.0412)
    hremyach = shapely.geometry.Point(52.3332, 33.2891)'''
)

st.markdown('''Next, we define the following functions:
 \n1) **create_line(date, df)** : Creates a line for a particular date in the dataframe
\n2) **create_east_polygon(line)** : Creates and returns a polygon for the *Eastern* front based on the line parameter
\n3) **create_north_polygon(line)** : Creates and returns a polygon for the *Northern* front based on the line parameter
\n4) **caclulate_area_diff(polygon1, polygon2)** : Calculates and returns the difference in area between the 2 polygons''')

def create_line(battle_date, battles_df):
    '''
      This function takes in a date and a  dataframe and creates a line for that date.
      create_geo_pandas_line(date, battles_df) -->  [line1, line2, line 3 ]
    '''

    # Create a GeoDataFrame of the points
    date_df = battles_df[battles_df['event_date'].isin([battle_date])]
    date_df = date_df[['latitude', 'longitude']]
    line = shapely.geometry.LineString(list(zip(date_df.longitude, date_df.latitude)))
    return line

def create_east_polygon(line):
    '''
      This function takes a line and creates a polygon for the eastern part of the front
      create_east_polygon(line) -->  \
      POLYGON ((37.9999 48.5956, 46.47747 30.73262, 44.58883 33.5224, 45.3607 36.4706, 47.09514 37.54131, ...))
    '''
    # Point gotten from https://latitudelongitude.org/ua/odessa/
    odessa = shapely.geometry.Point(46.47747, 30.73262) 
    
    # Point gotten from https://latitudelongitude.org/ua/sevastopol/
    sevastopol = shapely.geometry.Point(44.58883, 33.5224)
    
    # Point gotten from https://latitudelongitude.org/ua/kerch/
    kerch = shapely.geometry.Point(45.3607, 36.4706)
    
    # Point gotten from https://latitudelongitude.org/ua/mariupol/    
    mariupol = shapely.geometry.Point(47.09514, 37.54131) 
    
    # Point gotten from https://latitudelongitude.org/ua/luhansk/
    luhansk = shapely.geometry.Point(48.56705, 39.31706) 
    
    # Point gotten from https://latitudelongitude.org/ua/vovchansk/
    vovchansk = shapely.geometry.Point(50.29078, 36.94108)
    
    
    polygon_points = [list(line.coords)[i] for i in range(0, len(line.coords))]
    polygon_points.append(list(odessa.coords)[0])
    polygon_points.append(list(sevastopol.coords)[0])
    polygon_points.append(list(kerch.coords)[0])
    polygon_points.append(list(mariupol.coords)[0])
    polygon_points.append(list(luhansk.coords)[0])
    polygon_points.append(list(vovchansk.coords)[0])
    polygon = shapely.geometry.polygon.Polygon(polygon_points)
    
    return polygon


def create_north_polygon(line):
    '''
      This function takes a line and creates a polygon for the northern part of the front
      create_north_polygon(line) -->  
        POLYGON ((37.9999 48.5956, 46.47747 30.73262, 44.58883 33.5224, 45.3607 36.4706, 47.09514 37.54131, ...))
    '''
    
    # Point gotten from 
    # https://www.google.com/search?q=dobryanka+ukraine+longitude+and+latitude&ei=VmRoZMb9KZ6j5NoPwMC7eA&oq=dobryanka+ukraine+longitude&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAxgAMgUIIRCgATIFCCEQoAEyBQghEKABOgsIABCKBRCGAxCwA0oECEEYAVCTCVjTI2D3KmgBcAB4AIABgAGIAdAHkgEEMTIuMZgBAKABAcgBA8ABAQ&sclient=gws-wiz-serp
    dobryanka = shapely.geometry.Point(52.0601, 31.1837)
    
    # Point from 
    # https://www.google.com/search?q=seredyna+ukraine+longitude+and+latitude&ei=X2RoZInAG6Gm5NoP59uvwA4&ved=0ahUKEwjJ68WsnoP_AhUhE1kFHeftC-gQ4dUDCBE&uact=5&oq=seredyna+ukraine+longitude+and+latitude&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIFCAAQogQyBQgAEKIEMgUIABCiBDIFCAAQogQ6CwgAEIoFEIYDELADOgoIIRCgARDDBBAKSgQIQRgBUOMPWIoVYJIWaARwAHgAgAFfiAGvAZIBATKYAQCgAQKgAQHIAQLAAQE&sclient=gws-wiz-serp
    seredyna = shapely.geometry.Point(52.1837, 34.0412)
    
    # Point from
    # https://www.google.com/search?q=hremyach+ukraine+longitude+and+latitude&ei=mWRoZLeXLb-o5NoP892EsAU&ved=0ahUKEwj3x6vInoP_AhU_FFkFHfMuAVYQ4dUDCBE&uact=5&oq=hremyach+ukraine+longitude+and+latitude&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIFCAAQogQyBQgAEKIEOggIABCiBBCwAzoICCEQoAEQwwRKBAhBGAFQ4AJY_gZg5ApoAnAAeACAAWGIAcEBkgEBMpgBAKABAqABAcgBAsABAQ&sclient=gws-wiz-serp
    hremyach = shapely.geometry.Point(52.3332, 33.2891)
    
    
    polygon_points = [list(line.coords)[i] for i in range(0, len(line.coords))]
    polygon_points.append(list(dobryanka.coords)[0])
    polygon_points.append(list(hremyach.coords)[0])
    polygon_points.append(list(seredyna.coords)[0])
    polygon = shapely.geometry.polygon.Polygon(polygon_points)
    return polygon

def calculate_area_diff(polygon1, polygon2):
    '''
    This function calculate the area difference from one polygon from another
    calculate_area_diff(polygon1, polygon2) --> 4.9627030048339
    '''
    diff_1 = polygon1.buffer(.01) - polygon2.buffer(.01)
    diff_2 = polygon2.buffer(.01) - polygon1.buffer(.01)
    
    return diff_1.area + diff_2.area





# Seperate the northern front of the war from the eastern/southern fronts of the war
df_northern_front = df_battles_only[(df_battles_only['latitude'] >= 50.2826) 
                                    & (df_battles_only['longitude'] <= 35.0364)]

df_eastern_front = df_battles_only[(df_battles_only['latitude'] < 50.2826) 
                                   & (df_battles_only['longitude'] > 35.0364)]

# Gather all the dates for both fronts
battle_dates_north = df_northern_front['event_date'].unique()
battle_dates_east = df_eastern_front['event_date'].unique()

# Seperate/sort battle dates for the north
battle_dates_north = battle_dates_north[battle_dates_north < pd.to_datetime('04-07-22')]

# To CHECK CHECK
# st.write(battle_dates_north)
# battle_dates_north.sort()

# Create a list of the dataframes for each days worth of battles
battles_north = [df_northern_front[df_northern_front['event_date'].isin([battle_date])] 
                 for battle_date in battle_dates_north]
battles_east = [df_eastern_front[df_eastern_front['event_date'].isin([battle_date])] 
                for battle_date in battle_dates_east]

# Create a mechanism of identifying if the battles were a net gain or loss for the Ukrainians
max_lat_north = [battles_north[x]['latitude'].max() for x in range(len(battles_north))]
max_long_east = [battles_east[x]['longitude'].max() for x in range(len(battles_east))]
df_north_dir_vic = [0]
df_east_dir_vic = [0]

# If its a net positive for the Ukrainians i.e. the line moves East or North give it a 1 else -1
df_north_dir_vic += [-1 if max_lat_north[x] > max_lat_north[x-1] else 1 for x in range(1, len(battles_north))]
df_east_dir_vic += [1 if max_long_east[x] < max_long_east[x-1] else -1 for x in range(1, len(battles_east))]

# Create a list of the battle lines
battle_lines_north = [create_line(battle_dates_north[x], battles_north[x]) 
                      if len(battles_north[x]) > 1 
                      else create_line(battle_dates_north[x-1], battles_north[x-1]) for x in range(len(battles_north))]
battle_lines_east = [create_line(battle_dates_east[x], battles_east[x]) 
                     if len(battles_east[x]) > 1 
                     else create_line(battle_dates_east[x-1], battles_east[x-1]) for x in range(len(battles_east))]

# Create a a list of the polygons
battle_polygons_north = [create_north_polygon(line) for line in battle_lines_north]
battle_polygons_east = [create_east_polygon(line) for line in battle_lines_east]

# Calculate the difference from one day to the next
battle_difference_north =  [calculate_area_diff(battle_polygons_north[x], battle_polygons_north[x-1])  
                            if x > 0 else 0 for x in range(len(battle_polygons_north))]
battle_difference_east =  [calculate_area_diff(battle_polygons_east[x], battle_polygons_east[x-1])  
                           if x > 0 else 0 for x in range(len(battle_polygons_east))]

# Calcualte the difference again but include if it was the Ukrainians or Russians
battle_difference_north_dir =  [calculate_area_diff(battle_polygons_north[x], 
                                                    battle_polygons_north[x-1])*df_north_dir_vic[x]  
                                if x > 0 else 0 for x in range(len(battle_polygons_north))]
battle_difference_east_dir =  [calculate_area_diff(battle_polygons_east[x], 
                                                   battle_polygons_east[x-1])*df_east_dir_vic[x]  
                               if x > 0 else 0 for x in range(len(battle_polygons_east))]

# Calculate the total difference
battle_diff_north_tot = [sum(battle_difference_north_dir[:i+1]) for i in range(len(battle_difference_north_dir))]
battle_diff_east_tot = [sum(battle_difference_east_dir[:i+1]) for i in range(len(battle_difference_east_dir))]



st.markdown("After doing the required transformations, we plot the daywise difference in battle lines.")

# Compute differences on the eastern front and compute a zone column for the altair chart legend
diff_df = pd.DataFrame(
    {'date':battle_dates_east, 
     'conquered_difference':battle_difference_east , 
     'zone' : ['East' for i in range(len(battle_difference_east))]
    })


# Create chart for area differences on the eastern front
chart = alt.Chart(diff_df).mark_line(point=True).encode(
    x='date',
    y='conquered_difference',
    color='zone',
    tooltip=['date', alt.Tooltip('conquered_difference:Q', format='.3f', title='Difference (km²)')]
).properties(
    width=875,
    height=500,
    title='Area Diffference (in sq. km) by Day Eastern Front'
)

# Compute differences on the northern front and compute a zone column for the altair chart legend
diff_df_n = pd.DataFrame(
    {'date':battle_dates_north, 'conquered_difference':battle_difference_north, 
     'zone' : ['North' for i in range(len(battle_difference_north))]
    })

# Create chart for area differences on the northern front
chart2 = alt.Chart(diff_df_n).mark_line(point=True).encode(
    x='date',
    y='conquered_difference',
    color='zone',
    tooltip=['date', alt.Tooltip('conquered_difference:Q', format='.3f', title='Difference (km²)')]
).properties(
    width=875,
    height=500,
    title='Area Diffference (in sq. km) by Day Northern Front'
)

# Layer the chart
c = alt.layer(
    chart,chart2).properties(
    width=875,
    height=500,
    title='Area Difference (in sq. km) by Day Both Fronts'
)

st.altair_chart(c)

st.markdown('''**Figure 7**: The chart above shows the amount of area (in sq. km) the lines of battles have moved *daywise*. This is an absolute difference value and does not show who gained/lost.
It is clearly visible that the Northern territory was quickly regained by the Ukrainians. The difference on the Northern front is more than the Eastern front, even on the earlier days of the war.
The eastern front, over almost 11 months has very little difference in area, showing that the eastern front of the Russian attack has also remained pretty much stagnant / confined to a smaller area.''')

diff_df = pd.DataFrame({'date':battle_dates_east, 'conquered_difference':battle_difference_east_dir, 'Front' : ['East' for i in range(len(battle_difference_east))]})

chart = alt.Chart(diff_df).mark_line(point=True).encode(
    x='date',
    y='conquered_difference',
    color='Front',
    tooltip=['date', alt.Tooltip('conquered_difference:Q', format='.3f', title='Difference (km²)')]
).properties(
    width=840,
    height=500,
    title='Area Difference by Day Eastern Front'
)

diff_df_n = pd.DataFrame({'date':battle_dates_north, 'conquered_difference':battle_difference_north_dir, 'Front' : ['North' for i in range(len(battle_difference_north))]})

chart2 = alt.Chart(diff_df_n).mark_line(point=True).encode(
    x='date',
    y='conquered_difference',
    color='Front',
    tooltip=['date', alt.Tooltip('conquered_difference:Q', format='.3f', title='Difference (km²)')]
).properties(
    width=840,
    height=500,
    title='Area Difference by Day Northern Front'
)

zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red',size=2,opacity=0.5).encode(y='y')

map = alt.layer(
    chart,chart2,zero_line).properties(
    width=840,
    height=500,
    title='Area Difference by Day Both Fronts'
).interactive()

st.altair_chart(map)

st.markdown('''**Figure 8**: The chart above shows the amount of area (in sq. km) the lines of battles have moved *daywise*. This shows the value gained by each side. Positive gain implies Ukraine regained some territory whereas negative implies that Russia gained territory.
From this, we can identify that the Northern front had fierce battles initially, with Russia trying to capture the capital (Kyiv). This attack was quickly cut short by Ukraine (within 3 months).
The eastern front, over almost 11 months has very little difference in area, showing that the eastern front of the Russian attack has also remained pretty much stagnant / confined to an area. The line chart oscillates around 0, and shows that no side has been able to move too much, although Russia has been able to push into Ukraine a little.
''')

st.subheader("Plotting Battle lines by month")

st.markdown("Next, we aggregate the battle line movement by month, for each front of the battle.")
st.markdown("As we identified before, we make separate lines for East and Northern fronts and connect them separately using latitude and longitude respectively.")

# Create a copy of the battle dataset
df_battle_subset_by_month_copy = df_battle_subset_by_month.copy()

# Create a column for legend readability
df_battle_subset_by_month_copy['month_year'] = df_battle_subset_by_month_copy['event_date'].map(
    lambda x : str(x.month_name())+', '+str(x.year))

# Create a column for identifying if the battle was the northern front or not

# Create a column for identifying if the battle was the northern front or not
df_battle_subset_by_month_copy['northern_front'] = np.where(
    (df_battle_subset_by_month_copy['latitude'] >= 50.20) 
    & (df_battle_subset_by_month_copy['longitude'] <= 35.0364), 
    1, 0)

# Create battle lines, identify area gained or lost and assign a sign for the computed area difference (+ve for Ukrane and -ve for Russia).

# Gather all the dates for both fronts
battle_dates_month = df_battle_subset_by_month_copy['event_date'].unique()

# Create a list of the dataframes for each days worth of battles
battles_month = [df_battle_subset_by_month_copy[
    df_battle_subset_by_month_copy['event_date'].isin([battle_date])] for battle_date in battle_dates_month]

# Create a mechanism of identifying if the battles were a net gain or loss for the Ukrainians
max_long_month = [battles_month[x]['longitude'].max() for x in range(len(battles_month))]
df_month_dir_vic = [0]

# If its a net positive for the Ukrainians ie the line moves East or North give it a 1 o/w -1
df_month_dir_vic += [1 if max_long_month[x] < max_long_month[x-1] else -1 for x in range(1, len(battles_month))]

# Create a list of the battle lines
battle_lines_month = [create_line(battle_dates_month[x], battles_month[x]) if len(battles_month[x]) > 1 
                      else create_line(battle_dates_month[x-1], battles_month[x-1]) 
                      for x in range(len(battles_month))]

# Create a a list of the polygons
battle_polygons_month = [create_east_polygon(line) for line in battle_lines_month]

# Calculate the difference from one day to the next
battle_difference_month =  [calculate_area_diff(battle_polygons_month[x], 
                                                battle_polygons_month[x-1])*df_month_dir_vic[x]  
                            if x > 0 else 0 
                            for x in range(len(battle_polygons_month))]

# Store a dataframe to identify dates, zones and the difference monthwise.

# Create a dataframe for the Eastern front, aggregated by month
diff_df_month = pd.DataFrame(
    {'date':battle_dates_month, 
     'conquered_difference':battle_difference_month, 
     'zone' : ['East' for i in range(len(battle_difference_month))]
     })

# Group the data monthly.

# Group by formatted date
diff_df_month_grouped = diff_df_month.groupby(diff_df_month.date.dt.strftime('%B, %Y')
                                             )['conquered_difference'].sum().reset_index()

# get absolute value of calculated difference
diff_df_month_grouped['conquered_difference'] = diff_df_month_grouped['conquered_difference'].abs()


# Join with the battle dataset after obtaining month wise gain/loss value
df_battle_subset_by_month_copy = df_battle_subset_by_month_copy.merge(
    diff_df_month_grouped,
    how='left',
    left_on='month_year',
    right_on='date')

# Create 2 sub-dataframes
df_east = df_battle_subset_by_month_copy[df_battle_subset_by_month_copy['northern_front'] == 0]
df_north = df_battle_subset_by_month_copy[df_battle_subset_by_month_copy['northern_front']==1]

# Get the minimum and maximum of conquered difference for each of the fronts for altair plotting
east_max, east_min = df_east['conquered_difference'].max(),df_east['conquered_difference'].min()
north_max, north_min = df_north['conquered_difference'].max(),df_north['conquered_difference'].min()

# Source: https://altair-viz.github.io/gallery/interactive_legend.html

# Creating selectors for interactive map
selection = alt.selection_single(fields=['month_year'], bind='legend')
selection_n = alt.selection_single(fields=['month_year'], bind='legend')

# Creating the line for the Eastern front
line_east = alt.Chart(df_battle_subset_by_month_copy).mark_line(
).encode(
    order='latitude:O',
    latitude='latitude:Q',
    longitude='longitude:Q',
    strokeWidth=alt.StrokeWidth('conquered_difference:Q', 
                                scale=alt.Scale(domain=[east_min, east_max], range=[5, 1])),
    color=alt.Color('month_year:O', scale=alt.Scale(scheme='goldred'),sort=['event_date']),
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).project(
    type='mercator',
    scale=1100,
    center=[31, 49]
).properties(
    width=700,
    height=500,
).add_selection(selection).transform_filter(alt.datum.northern_front == 0)

# Creating the line for the Northern front
line_north = alt.Chart(df_battle_subset_by_month_copy).mark_line().encode(
    order='longitude:O',
    latitude='latitude:Q',
    longitude='longitude:Q',
    strokeWidth=alt.StrokeWidth('conquered_difference:Q', 
                                scale=alt.Scale(domain=[north_min, north_max], range=[5, 1])),
    color=alt.Color('month_year:O', scale=alt.Scale(scheme='goldred'),sort=['event_date']),
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).project(
    type='mercator',
    scale=1100,
    center=[31, 49]
).properties(
    width=700,
    height=500,
).add_selection(selection_n).transform_filter(alt.datum.northern_front == 1)

map = base + line_east

#Remove map edge borders
map.configure_view(stroke=None)

map

st.markdown('''**Figure 9**: This chart shows the Eastern front battle lines by month. The stroke width (thickness) of the line is inversely proportional to the absolute area gained or lost.
This means thicker lines would imply that the no side has moved the line of battle in their favour.
This map is interactive. Clicking the legend item changes the map value so the user can identify the line for the month.
We can also see as the war progresses, the battle line keeps getting shorter, implying there are lesser battles over month.''')

# layer the maps and sort the legend
map = alt.layer(base,line_east,line_north
               ).encode(
    alt.Color('month_year:O', scale=alt.Scale(scheme='goldred'),sort=['event_date']))

# Remove map edge borders
map.configure_view(stroke=None)
map

st.markdown('''**Figure 10**: This chart shows the Northen and Eastern front battle lines by month. The stroke width (thickness) of the line is inversely proportional to the absolute area gained or lost.
This means thicker lines would imply that the no side has moved the line of battle in their favour.
This map is interactive. Clicking the legend item changes the map value so the user can identify the line for the month.
The Northern front was quickly recovered by the Ukrainians, hence there are no North battle lines after April 2022.''')

st.header("Equipment Losses and Casualty Data")

st.markdown("The charts below identifies the losses encountered by the Russians daywise during the battle. The losses dataset contains information on tanks, field artillery, anti aircraft weapons, drones, aircrafts and personnel too.")

data_path = path.joinpath('Data')
russia_losses = data_path.joinpath('russia_losses_equipment.csv')
russia_losses_p = data_path.joinpath('russia_losses_personnel.csv')
battle_data = data_path.joinpath('acled_battle_data_23Feb.csv')

maps = data_path.joinpath("ukraine_geojson-master")
ukraine_map_path = maps.joinpath("UA_FULL_Ukraine.geojson")

df_equipment = pd.read_csv(russia_losses, sep=',')
df_personnel = pd.read_csv(russia_losses_p, sep=',')
df_battle = pd.read_csv(battle_data, sep=',')


# Define a function that takes in a dataframe to convert the data to identify day wise losses encountered by the Russians. The Kaggle dataset contains cumulative losses. We use this function to identify losses day wise.
def convert_data(df):
    '''
    Convert data of the dataframe entered
    '''
    def convert_cumulative_to_daywise(col_name):
        '''
        Convert cumulative columns to daywise by subtracting i row from (i+1) row value and
        '''

        #The meaning of biufc: b bool, i int (signed), u unsigned int, f float, c complex
        if df[col_name].dtype.kind in 'biufc':
            return df[col_name] - df[col_name].shift()
      
        else:
            return df[col_name]

    return convert_cumulative_to_daywise


# Initialize and clean the equipment data

# Initializing the data transformer function to equipment dataframe
equiment_count_transformer = convert_data(df_equipment)

# Create an empty dataframe to store counts by day
df_equipment_by_day = pd.DataFrame()

#Extracting date and day columns and the columns we need to loop over to compute daywise values
day, date, *equipment_loss_cols = df_equipment.columns

# Keeping day and date column identical
df_equipment_by_day[day] = df_equipment[day]
df_equipment_by_day[date] = df_equipment[date]

# Convert cumulative count to daywise count
for col_name in equipment_loss_cols:
    df_equipment_by_day[col_name] = equiment_count_transformer(col_name)
    print('{} column processed successfully'.format(col_name))

#Keeping the first row same as the original since shift sets the first row data to 0
df_equipment_by_day.iloc[0] = df_equipment.iloc[0]

# Initialize and clean the personnel data
# Initialize data transformer function with personnel dataset
personnel_count_transformer = convert_data(df_personnel)

# Initialize an empty dataframe
df_personnel_by_day = pd.DataFrame()

#Extracting date and day columns and the columns we need to loop over to compute daywise values
date, day, *personnel_loss_cols = df_personnel.columns

# Keep day and date columm identical
df_personnel_by_day[date] = df_personnel[date]
df_personnel_by_day[day] = df_personnel[day]

# Transform cumulative count to day wise count
for col_name in personnel_loss_cols:
    df_personnel_by_day[col_name] = personnel_count_transformer(col_name)
    print('{} column processed successfully'.format(col_name))

# Keeping the first row same as the original data since shift sets the first row data to 0
df_personnel_by_day.iloc[0] = df_personnel.iloc[0]

st.subheader("Tanks & Field Artillery")

# Create the tank dataframe
df_tank = df_equipment_by_day[['day','tank']].copy()

# Create the field artillery dataframe
df_fa = df_equipment_by_day[['day','field artillery']].copy()

# Add a column for altair legend coloring
df_tank['category'] = ['Tank' for i in range(len(df_tank))]
df_fa['category'] = ['Field Artillery' for i in range(len(df_fa))]

# Create a selection objection for each of the charts
selection_tank = alt.selection_single(fields=['category'], bind='legend')
selection_fa = alt.selection_single(fields=['category'], bind='legend')

# Create the line chart for tanks
tank = alt.Chart(df_tank).mark_line(point=True).encode(
    x= 'day',
     y= 'tank',
      color=alt.Color('category:O',scale=alt.Scale(scheme='dark2')),
      opacity=alt.condition(selection_tank, alt.value(1), alt.value(0))      
      ).add_selection(selection_tank)

# Create the line chart for field artillery
FA = alt.Chart(df_fa).mark_line(point=True).encode(
    x= 'day', 
    y= 'field artillery',
    color='category:O',
    opacity=alt.condition(selection_fa, alt.value(1), alt.value(0))
    ).add_selection(selection_fa)

# Create a layered map
land_losses = alt.layer(tank, FA).properties(height = 400 , width=900, title="Tanks and Field Artillery losses by day of war").interactive()

st.altair_chart(land_losses)

st.markdown('''**Figure 11** : The line chart above shows the losses of Tanks and Field Artillery by the Russian Army. 
The inital spike is due to the battle being on both fronts, which were not successful.
\n The map is interactive, click on the legend to explore each line individually.''')

st.subheader("Multi-Rocket Systems")

mrs = alt.Chart(df_equipment_by_day).mark_line(point=True).encode(x= 'day', y= 'MRL').properties(
    height = 400 , width=850, title="Multi-Rocket Systems losses by day of war").interactive()
mrs

st.markdown("**Figure 12** : The line chart above shows the losses of Multi-Rocket System by the Russian Army.")

st.subheader("Anti-aircraft Weapons")

aaw = alt.Chart(df_equipment_by_day).mark_line(point=True).encode(x= 'day', y= 'anti-aircraft warfare').properties(
    height = 400 , width=850, title="Anti-aircraft weapons losses by day of war").interactive()

st.altair_chart(aaw)

st.markdown("**Figure 13** : The line chart above shows the losses of Anti-aircraft weapons by the Russian Army.")

st.subheader("Drones and Aircrafts")

# Create the aircraft dataframe
df_aircraft = df_equipment_by_day[['day','aircraft']].copy()

# Create the drones dataframe
df_drone = df_equipment_by_day[['day','drone']].copy()

# Add a column for altair legend coloring
df_aircraft['category'] = ['Aircraft' for i in range(len(df_aircraft))]
df_drone['category'] = ['Drone' for i in range(len(df_drone))]

# Create a selection objection for each of the charts
selection_aircraft = alt.selection_single(fields=['category'], bind='legend')
selection_drone = alt.selection_single(fields=['category'], bind='legend')


# Create the line chart for aircrafts
aircraft = alt.Chart(df_aircraft).mark_line(point=True).encode(
    x= 'day',
     y= 'aircraft',
      color=alt.Color('category:O',scale=alt.Scale(scheme='dark2')),
      opacity=alt.condition(selection_aircraft, alt.value(1), alt.value(0))      
      ).add_selection(selection_aircraft)

# Create the line chart for drones
drone = alt.Chart(df_drone).mark_line(point=True).encode(
    x= 'day', 
    y= 'drone',
    color='category:O',
    opacity=alt.condition(selection_drone, alt.value(1), alt.value(0))
    ).add_selection(selection_drone)

# Create a layered map
air_losses = alt.layer(aircraft, drone).properties(
    height = 400 , width=900, title="Aircraft & Drones losses by day of war").interactive()

st.altair_chart(air_losses)

st.markdown('''**Figure 14** : The line chart above shows the losses of Drones and Aircrafts by the Russian Army. 
We can see as the Russian offensive failed, there has been a significant increase in drone usage for remote explosions and warfare.''')
st.subheader("Personnel")

p = alt.Chart(df_personnel_by_day).mark_line(point=True).encode(x= 'day', y= 'personnel').properties(
    height = 400 , width=850, title="Personnel losses by day of war")
p

st.markdown('''**Figure 15** : The line chart above shows the losses of personnel by the Russian Army. The eventual steady increase could indicate Russian attempts at 
            moving the Battle lines into Ukraine, but failing to do so.''')

st.markdown('''An interesting thing to note here is that the cost of offence is extremely high. Most of the graphs depict a significant spikes in losses at the initial attempt to take the Ukranian capital. 
Russia has not been able to attain air supremacy due to the significant losses of their aircrafts in the initial attack and 
have resorted more to drones as the war progressed.
Considering the land attacks, we can also see that the Russian losses in tanks and field artillery are extremely high in the initial attacks.
''')


st.header('Conclusion')


st.markdown("From the evidence presented, it is clear that Russia's ability to "+
            "conduct offensive warfare is limited by its ability to resupply its ammunition and personnel."+ 
            " Ukraine's upcoming spring/summer offensive may help address these questions, however recent analysis "+ 
            "suggests it will not be decisive enough to bring the war to a swift end. Our methodology of measuring the stability of "+ 
            "the line will be critical in determining the outcome of this war. If defensive warfare is dominant over offensive warfare, "+
            "then the war in Ukraine could potentially last for years. This means Western powers must be prepared to support the Ukrainian "+
           " war effort for the long-term, and Taiwan should also be armed and supported to deter China from an invasion.")

st.subheader('Acknowledgements and Sources')

# Meeting with Jonathan Caulkins. Memo present in folder 

st.markdown('''Code sources:
\n* https://stackoverflow.com
\n* https://geopandas.org/en/stable/docs.html
\n* https://shapely.readthedocs.io/en/stable/
\n
Altair Maps:
\n * https://altair-viz.github.io/altair-tutorial/notebooks/09-Geographic-plots.html
\n* https://altair-viz.github.io/altair-tutorial/notebooks/06-Selections.html
\n
Datasets:
\n* https://acleddata.com
\n* https://www.kaggle.com/datasets/piterfm/2022-ukraine-russian-war''')

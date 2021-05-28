
import streamlit as st

import psycopg2
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn 
import datetime 
import io

engine = create_engine('postgres://dennisssekamaanya:dennis123@localhost:5432/dennisssekamaanya')

st.write('''
# Analyzing Delayed Flight Data!
Let's use this amazing app to expore and analyze our flight dataset
''')

#GENERAL SAMPLE STATS BY AIRLINE

st.checkbox('Show/Clear', True, key = 2)
st.sidebar.markdown('General Stats by Airline')
side_button1 = st.sidebar.button('10 Worst Airline Performers')

if side_button1: 
    gen_data1 = pd.read_sql_query('''SELECT airline, AVG(departure_delay) as Dep_Delay, AVG(air_system_delay) as AirSys_Delay, AVG(security_delay) as Security_Delay, 
    AVG(airline_delay) as Airline_Delay, AVG(late_aircraft_delay) as Aircraft_Delay, AVG(weather_delay) as Weather_Delay  
    FROM "flight_data" 
    GROUP BY airline''', con = engine)
    st.dataframe(gen_data1)

    fig1, ax1 = plt.subplots(figsize=(15,8))
    ax1.plot('airline', 'dep_delay', data = gen_data1)
    ax1.plot('airline', 'airsys_delay', data = gen_data1)
    ax1.plot('airline', 'security_delay', data = gen_data1)
    ax1.plot('airline', 'airline_delay', data = gen_data1)
    ax1.plot('airline', 'aircraft_delay', data = gen_data1)
    ax1.plot('airline', 'weather_delay', data = gen_data1)
    ax1.legend(['Departure Delay', 'Air-System Delay', 'Security Delay', 'Airline Delay', 'Late Aircraft Delay', 'Weater'], loc = 0)
    ax1.set_xlabel('AIRLINES')
    ax1.set_ylabel('MEAN DEPARTURE DELAY(MIN)')
    ax1.grid(color = 'b', b = True)
    st.pyplot(fig1)
    
#GENERAL STATS BY AIRPORT (SNAPSHOT OF 10)

st.sidebar.markdown('General Stats by Airport')
side_button2 = st.sidebar.button('10 Worst Airport Performers')
if side_button2:
    gen_data2 = pd.read_sql('''
    SELECT origin_airport, AVG(departure_delay) AS Mean_DepDelay, AVG(taxi_out) as Mean_TaxiOut, AVG(air_system_delay) as AirSys_Delay, AVG(security_delay) AS Security_Delay, AVG(airline_delay) AS Airline_Delay, 
    AVG(late_aircraft_delay) AS Aircraft_Delay, AVG(weather_delay) AS Weather_Delay FROM flight_data
    GROUP BY origin_airport
    ORDER BY Mean_DepDelay desc
    LIMIT 10''', con = engine)
    st.dataframe(gen_data2)

    
    fig2, ax2 = plt.subplots(figsize = (15,8))
    w = 0.2
    g1 = np.arange(len(gen_data2['origin_airport']))
    g2 = [i+w for i in g1]
    g3 = [i+w for i in g2]
    g4 = [i+w for i in g3]
    g5 = [i+w for i in g4] 
    g6 = [i+w for i in g5]
    g7 = [i+w for i in g6]
    x1 = ax2.bar('origin_airport','mean_depdelay', w, data = gen_data2)
    x2 = ax2.bar(g2, 'mean_taxiout', w, data = gen_data2)
    x3 = ax2.bar(g3, 'airsys_delay', w, data = gen_data2)
    x4 = ax2.bar(g4, 'security_delay', w, data = gen_data2)
    #x5 = ax2.bar(g5, 'airline_delay', w, data = gen_data2)
    #x6 = ax2.bar(g6, 'aircraft_delay', w, data = gen_data2)
    x7 = ax2.bar(g7, 'weather_delay', w,data = gen_data2)
    plt.grid()
    ax2.legend(['Mean Departure Delay', 'Mean Taxi-Out', 'Air-System Delay', 'Security Delay', 'Airline Delay', 
    'Late Aircraft Delay', 'Weather Delay'], loc = 0)
    ax2.set_xlabel('DEPARTURE AIRPORT')
    ax2.set_ylabel('MEAN AIRPORT DELAY(MIN)')
    ax2.set_xticklabels(gen_data2['origin_airport'], rotation=90)
    fig2.tight_layout()
    st.pyplot(fig2)

#DIRECT QUERY INPUTś

#DEFINE QUERY BUILDER. WE'LL NEED THIS ONE IN ORDER TO CONSTRUCT USER-INPUTS INTO AN SQL QUERY

def query_builder1(userChoice_, features_, groupbyParam_):
    select_string = ""
    if len(features_)==1:
        select_string += "AVG({}) AS {}".format(features_[0])
    else:
        for i, feature_ in enumerate(features_):
            if i == len(features_)-1:
                select_string += "AVG({}) AS {}".format(feature_, feature_)
            else:
                select_string += "AVG({}) AS {}, ".format(feature_, feature_)
    #PIECING THE SELECT QUERY TOGETHER:
    print(select_string)
    select_segment = "SELECT {}, {} ".format(groupbyParam_[0], select_string)
    from_segment = 'FROM flight_data '
    where_segment = "WHERE origin_name = '{}'".format(userChoice_[0])
    groupby_segment = " GROUP BY {}".format(groupbyParam_[0])
    final_query = select_segment + from_segment + where_segment + groupby_segment
    return final_query 



#1. DEPARTURE DELAY BY AIRPORT
col1a, col1b = st.beta_columns(2)
expander1 = col1a.beta_expander('Departure Delay by Airport')
airport_from = expander1.multiselect('Select Airport', pd.read_sql_query('SELECT DISTINCT(origin_name) FROM "flight_data"', con = engine))
expander1a = col1b.beta_expander('Analyze By:')
to_analyze_by = expander1a.multiselect('Select stats', ('month', 'airline', 'departure_delay', 'taxi_out','arrival_delay','taxi_in', 'air_system_delay', 'security_delay', 'airline_delay', 'late_aircraft_delay', 'weather_delay'))
groupbyFeature = to_analyze_by[:1]
selectFeatures = to_analyze_by[1:]
finishedQuery = query_builder1(airport_from, selectFeatures, groupbyFeature)
print(finishedQuery)
stats_table = pd.read_sql_query(finishedQuery, con = engine)

# VISUALIZE THE DATA
livebutton1 = expander1a.button('Show Graph')
if livebutton1:
    fig3, ax3 = plt.subplots()
    for item in selectFeatures:
        ax3.plot(groupbyFeature[0], item, data = stats_table)
    ax3.set_title('DELAY STATS ON {}'.format(airport_from[0]))
    ax3.set_xlabel(groupbyFeature[0])
    ax3.set_ylabel('MEAN DELAY(MINUTES)')
    ax3.legend(selectFeatures)
    st.pyplot(fig3)






#2. ARRIVAL DELAY BY AIRPORT

col2a, col2b = st.beta_columns(2)
expander2 = col2a.beta_expander('Arrival Delay by Airport')
airport_to = expander2.multiselect('Select Airport', pd.read_sql_query('SELECT DISTINCT(dest_name) FROM flight_data', con = engine))
expander2b = col2b.beta_expander('Analyze By:')
to_analyze_by = expander2b.multiselect('Select Stats', ('departure_delay', 'taxi_out', 'air_system_delay', 'security_delay', 'airline_delay', 'late_aircraft_delay', 'weather_delay'))


#3. ROUTE ANALYSIS

col3a, col3b, col3c, col3d = st.beta_columns(4)
expander3a = col3a.beta_expander('By Route')
carr_select = expander3a.selectbox('Choose Airline', pd.read_sql_query('SELECT DISTINCT(airline) FROM flight_data', con = engine))
expander3b = col3b.beta_expander('Departure Airport')
flying_from = expander3b.selectbox('From: Select Airport', pd.read_sql_query("SELECT DISTINCT(origin_airport) FROM flight_data WHERE airline = '%s'" %(carr_select), con = engine))
expander3c = col3c.beta_expander('Destination Airport')
flying_to = expander3c.selectbox('To: Select Airport', pd.read_sql_query("SELECT DISTINCT(destination_airport) FROM flight_data WHERE airline = '%s' AND origin_airport = '%s'" %(carr_select,flying_from), con = engine))
expander3d = col3d.beta_expander('Analyze By:')
metric_select = expander3d.multiselect('Select Stats;', ('month', 'departure_delay', 'arrival_delay', 'air_system_delay', 'airline_delay', 'late_aircraft_delay', 'weather_delay'))





    

    
import streamlit as st
import requests
import time
import json
from datetime import datetime, date
from streamlit_folium import st_folium
import folium
import pandas as pd
from streamlit_elements import elements, mui, html
from streamlit_elements import dashboard

# API keys
OPENWEATHER_API_KEY = "2341866a33e6f42c7b76a75c179f72f9"
WEATHERBIT_API_KEY = "9ea15608f9954dae8dd8de27e39e4f1d"

# Function to get current and forecast weather data
def get_weather_data(city_name, unit_symbol):
    if unit_symbol == "K":
        api_unit = 'standard'
    elif unit_symbol == "℉":
        api_unit = 'imperial'
    else:
        api_unit = "metric"

    weather_response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units={api_unit}"
    ).json()

    weather_response['ForecastData'] = requests.get(
        f"https://api.weatherbit.io/v2.0/forecast/daily?city={city_name}&days=12&units={api_unit[0].capitalize()}&key={WEATHERBIT_API_KEY}"
    ).json()

    return weather_response

# Function to get historical weather data
def get_forecast_data(city_name, unit_symbol):
    current_date = date.today()
    if unit_symbol == "K":
        unit_code = 'S'
    elif unit_symbol == "℉":
        unit_code = 'I'
    else:
        unit_code = "M"

    start_date = f"{current_date.year}-{current_date.month}-{current_date.day - 1}"
    end_date = f"{current_date.year}-{current_date.month}-{current_date.day + 5}"

    historical_response = requests.get(
        f"https://api.weatherbit.io/v2.0/history/daily?city={city_name}&start_date={start_date}&end_date={end_date}&units={unit_code}&key={WEATHERBIT_API_KEY}"
    ).json()

    return historical_response

# Function to get city name from coordinates
def get_city_by_coordinates(latitude, longitude):
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&accept-language=en&addressdetails=1&zoom=10",
            headers={"User-Agent": "Mozilla/5.0"}
        ).json()
        return response['address']['city']
    except:
        return False

# Load city/region list
with open(r"regions.json", "r") as file:
    city_list = json.load(file)

# Current time
current_time = datetime.now()
formatted_time = current_time.strftime("%H:%M:%S")

# Set page config
st.set_page_config(page_title="Weather DASMBLARK", layout="wide")
st.write("by group3 class 7/2")
sidebar = st.sidebar

# Status while loading
status = st.status("Collecting Data ...", expanded=True, state="running")
get_city_by_coordinates(10.7769, 106.7009)

with sidebar:
    st.title("🌈Advanced Weather Forecasting App")

    # City selection dropdown
    selected_city_option = st.selectbox("🌆Select City", placeholder="Choose a city", options=city_list)
    selected_city = selected_city_option

    # Display map with marker
    city_map = folium.Map(location=[21.0285, 105.8542], zoom_start=16)
    folium.Marker(
        [21.0285, 105.8542],
        popup="Hanoi",
        tooltip="Hanoi"
    ).add_to(city_map)

    # Unit selection
    selected_unit = st.selectbox("🌡️Select Unit", options=["℃", "℉", "K"])

    # Analyse button
    analyse_clicked = st.button("Analyse", help="Start analysing the selected city")

    # API Badges
    st.markdown(
        """:green-badge[**✔ OpenWeatherAPI**]
        :orange-badge[**✔ WeatherbitAPI**]
        :violet-badge[**✔ Python 3.12**]
        :blue-badge[**✔ Streamlit**]
        :violet-badge[:material/star: **Favorite**] 
        :red-badge[⚠️ **Needs review**]"""
    )

    # Feedback
    user_feedback = st.feedback("thumbs")

    # Map popup dialog to choose city
    @st.dialog("Choose Your City")
    def show_map_popup():
        map_result = st_folium(city_map, width=500, height=500)
        confirm_button = st.button("Confirm")
        if confirm_button and get_city_by_coordinates(map_result['last_clicked']['lat'], map_result['last_clicked']['lng']):
            st.session_state["selected_city"] = get_city_by_coordinates(map_result['last_clicked']['lat'], map_result['last_clicked']['lng'])
            st.success("Location confirmed!")
        else:
            st.warning("This location is not supported.")

    # Open map selection if "Choose from map" selected
    if selected_city_option == "Choose from map" and not analyse_clicked:
        show_map_popup()

    # Use selected city from map if available
    if "selected_city" in st.session_state and selected_city_option == "Choose from map":
        selected_city = st.session_state["selected_city"]

if analyse_clicked:
    with status:
        st.write("Searching for data...")
        data = get_weather_data(selected_city,selected_unit)
        st.write("Found URL.")
        Main_data = get_forecast_data(selected_city, selected_unit)
        st.write("Downloading data...")
        dataframe = pd.DataFrame({
            "Temperatures" : [
    data["ForecastData"]['data'][0]['temp'],
    data["ForecastData"]['data'][1]['temp'],
    data["ForecastData"]['data'][2]['temp'],
    data["ForecastData"]['data'][3]['temp'],
    data["ForecastData"]['data'][4]['temp'],
    data["ForecastData"]['data'][5]['temp'],
    data["ForecastData"]['data'][6]['temp'],
    data["ForecastData"]['data'][7]['temp'],
    data["ForecastData"]['data'][8]['temp'],
    data["ForecastData"]['data'][9]['temp'],
    data["ForecastData"]['data'][10]['temp'],
],
            'Dates' : [
    data["ForecastData"]['data'][0]['datetime'],
    data["ForecastData"]['data'][1]['datetime'],
    data["ForecastData"]['data'][2]['datetime'],
    data["ForecastData"]['data'][3]['datetime'],
    data["ForecastData"]['data'][4]['datetime'],
    data["ForecastData"]['data'][5]['datetime'],
    data["ForecastData"]['data'][6]['datetime'],
    data["ForecastData"]['data'][7]['datetime'],
    data["ForecastData"]['data'][8]['datetime'],
    data["ForecastData"]['data'][9]['datetime'],
    data["ForecastData"]['data'][10]['datetime'],
]

        })
        status.update(label="Complete", expanded=False, state='complete')
    status.empty()
    try:
        icon_code = data["ForecastData"]['data'][0]['weather']['icon']
        icon_url = f"https://www.weatherbit.io/static/img/icons/{icon_code}.png"
        st.markdown(f"""
    <img src="{icon_url}" width="100" style="vertical-align: middle; margin-right: 10px;">
    <b style="font-size: 65px;">Current Weather in {selected_city} ({formatted_time})</b>
    """, unsafe_allow_html=True)
    except:
        st.markdown(f"""
    <b style="font-size: 65px;">Current Weather in {selected_city} ({formatted_time})</b>
    """, unsafe_allow_html=True)
    st.write(f"timezone: {data["timezone"]}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️Temperature:", f"{data['main']['temp']}{selected_unit}",str(round((data['main']['temp']) - (Main_data["data"][0]["temp"]),2)))
    col2.metric("🌡️Max Temperature:", f"{data['main']['temp_max']}{selected_unit}",str(round((data['main']['temp_max']) - (Main_data["data"][0]["max_temp"]),2)))
    col3.metric("🌡️Min Temperature:", f"{data['main']['temp_min']}{selected_unit}",str(round((data['main']['temp_min']) - (Main_data["data"][0]["min_temp"]),2)))
    col4.metric("🌡️Feel like:", f"{data['main']['feels_like']}{selected_unit}")
    col1.metric("💨Wind speed:", f'{data['wind']["speed"]} mph',str(round((data['wind']['speed']) - (Main_data["data"][0]["wind_spd"]),2)))
    col2.metric("💨Wind gust speed:", f'{Main_data['data'][1]['wind_gust_spd']} m/s',str(round((Main_data['data'][1]['wind_gust_spd'] - Main_data['data'][0]["wind_gust_spd"]),2)))
    col3.metric("💨Wind direction:",f'{Main_data['data'][1]['wind_dir']}',str(round((Main_data['data'][1]['wind_dir'] - Main_data['data'][0]['wind_dir']),2)))
    col1.metric("💧Humidity:",f'{data['main']['humidity']} mph')
    col2.metric("☁️Cloudliness:",f'{data['clouds']['all']} %',str(round((data['clouds']['all']) - (Main_data["data"][0]["clouds"]),2)))
    col3.metric('Pressure:',f'{data['main']['pressure']} hPa',str(round((data['main']['pressure']) - (Main_data["data"][0]["pres"]),2)))
    col4.metric('Sea level:',f'{data['main']['sea_level']} hPa')
    con1 ,con2, con3 ,con4 = st.columns(4)
    con1.markdown(f'''
    - Coordinate:
        + longitude: {data['coord']['lon']}  
        + latitude : {data['coord']['lat']}
    ''')
    con2.markdown(f'''
    - Day/Night:
        + Sunrise: {datetime.utcfromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S')}  
        + Sunset: {datetime.utcfromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')}
    ''')

    with st.container():
        st.markdown(f'''<b style="font-size: 45px;">5-days Weather Forecast</b>''', unsafe_allow_html=True)
        st.bar_chart(dataframe, x = 'Dates', y= "Temperatures",horizontal = True)
        with elements("weather_dashboard"):
            layout = [
                dashboard.Item(f"day_{i}", i % 4 + i*2, i // 4 + i * 2, 3, 2) for i in range(5)
            ]

            with dashboard.Grid(layout):
                for i in range(5):
                    forecast = data["ForecastData"]['data'][i]
                    date_str = forecast['datetime']
                    icon = forecast['weather']['icon']
                    icon_url = f"https://www.weatherbit.io/static/img/icons/{icon}.png"
                    temp = forecast['temp']
                    description = forecast['weather']['description'].capitalize()
                    humidity = forecast['rh']
                    wind = forecast['wind_spd']
                    clouds = forecast['clouds']

                    with mui.Card(key=f"day_{i}", sx={"p": 2, "borderRadius": "16px", "boxShadow": 3}):
                        mui.CardContent([
                            mui.Typography(f"{date_str}", variant="h6"),
                            html.img(src=icon_url, style={"width": "60px"}),
                            mui.Typography(f"{temp} {selected_unit}", variant="h5", sx={"fontWeight": "bold"}),
                            mui.Typography(description, variant="body2"),
                            mui.Typography(f"💧 {humidity}% humidity", variant="body2"),
                            mui.Typography(f"💨 {wind} m/s wind", variant="body2"),
                            mui.Typography(f"☁️ {clouds}% clouds", variant="body2"),
                        ])

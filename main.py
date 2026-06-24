import os
from PIL import Image 
import datetime as dt 
import requests as rq
import streamlit as st

if "current_screen" not in st.session_state:
    st.session_state.current_screen = "home"

if st.session_state.current_screen == "time":
    dynamic_title = "Iris: Date & Time"
elif st.session_state.current_screen == "weather":
    dynamic_title = "Iris: Weather"
elif st.session_state.current_screen == "daily_weather":
    dynamic_title = "Iris: Daily Weather"
elif st.session_state.current_screen == "hourly_weather":
    dynamic_title = "Iris: Hourly Weather"
elif st.session_state.current_screen == "todo":
    dynamic_title = "Iris: To Do"
elif st.session_state.current_screen == "notes":
    dynamic_title = "Iris: Notes"
elif st.session_state.current_screen == "email":
    dynamic_title = "Iris: Email"
elif st.session_state.current_screen == "forms":
    dynamic_title = "Iris: Forms"
else:
    dynamic_title = "Iris"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(SCRIPT_DIR, 'iris-circle-icon.png')
app_icon = Image.open(logo_path)

st.set_page_config(
    page_title=dynamic_title,
    page_icon=app_icon, 
    layout="wide"
)
        
st.markdown(
    """
    <style>
        html, body, [class*="css"], .stApp, h1, h2, h3, p {
            font-family: 'Atkinson Hyperlegible', sans-serif !important;
        }

        h1 { font-size: 120px !important; font-weight: bold !important; line-height: 1.1 !important; }
        h2 { font-size: 100px !important; font-weight: bold; text-align: center !important; }
        h3 { font-size: 80px !important; }

        button[data-testid="baseButton-secondary"], 
        button[data-testid="baseButton-primary"],
        .stButton button,
        div.stButton > button {
            border-radius: 15px !important;
            min-height: 150px !important;
        }

        button[data-testid="baseButton-secondary"] p,
        button[data-testid="baseButton-primary"] p,
        .stButton button p,
        div.stButton > button p {
            font-family: 'Atkinson Hyperlegible', sans-serif !important;
            font-size: 100px !important;  
            font-weight: bold !important;
        }

        hr {
            border: 0 !important;
            height: 6px !important;
            background-color: #333 !important; 
            margin-top: 10px !important;
            margin-bottom: 30px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.current_screen == "home":
    st.markdown("<h1>Iris: Lighting Up the Digital World</h1>", unsafe_allow_html=True)
    st.write("---")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        if st.button("⏰ Time", use_container_width=True):
            st.session_state.current_screen = "time"
            st.rerun()

    with row1_col2:
        if st.button("🌤️ Weather", use_container_width=True):
            st.session_state.current_screen = "weather"
            st.rerun()

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        if st.button("📝 To Do", use_container_width=True):
            pass

    with row2_col2:
        if st.button("📓 Notes", use_container_width=True):
            pass

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        if st.button("📧 Email", use_container_width=True):
            pass

    with row3_col2:
        if st.button("📋 Forms", use_container_width=True):
            pass

elif st.session_state.current_screen == "time":
    st.markdown("<h1>Date & Time</h1>", unsafe_allow_html=True)
    st.write("---")

    current_date = dt.datetime.now().strftime("%A, %B %d")
    current_time = dt.datetime.now().strftime("%I:%M %p")

    st.markdown(f"<h2>{current_date}</h2>", unsafe_allow_html=True)
    st.write("")
    st.markdown(f"<h2>{current_time}</h2>", unsafe_allow_html=True) 
    st.write("---")

    if st.button("⬅️ Back"):
        st.session_state.current_screen = "home"
        st.rerun()

elif st.session_state.current_screen == "weather":
    def get_weather():
        try:
            ip_api = rq.get("http://ip-api.com/json/")
            if ip_api.status_code == 200:
                ip_data = ip_api.json()
                lon = ip_data.get("lon")
                lat = ip_data.get("lat")

                weather_api = rq.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_direction_10m,wind_speed_10m,rain,showers&timezone=auto&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch")

                if weather_api.status_code == 200:
                    weather_data = weather_api.json()              
                    
                    temp = weather_data["current"]["temperature_2m"]
                    humidity = weather_data["current"]["relative_humidity_2m"]
                    app_temp = weather_data["current"]["apparent_temperature"]
                    wind_direction = weather_data["current"]["wind_direction_10m"]
                    wind_speed = weather_data["current"]["wind_speed_10m"]
                    rain = weather_data["current"]["rain"]
                    shower = weather_data["current"]["showers"]
                    
                    return temp, humidity, app_temp, wind_direction, wind_speed, rain, shower
        except Exception:
            pass
        return 0, 0, 0, 0, 0, 0, 0

    temp, humidity, app_temp, wind_direction, wind_speed, rain, shower = get_weather()

    if wind_direction <= 22.5 or wind_direction > 337.5:
        direction = "north"
    elif wind_direction >= 22.5 and wind_direction < 67.5:
        direction = "northeast"
    elif wind_direction >= 67.5 and wind_direction < 112.5:
        direction = "east"
    elif wind_direction >= 112.5 and wind_direction < 157.5:
        direction = "southeast"
    elif wind_direction >= 157.5 and wind_direction < 202.5:
        direction = "south"
    elif wind_direction >= 202.5 and wind_direction < 247.5:
        direction = "southwest"
    elif wind_direction >= 247.5 and wind_direction < 292.5:
        direction = "west"
    elif wind_direction >= 292.5 and wind_direction < 337.5:
        direction = "northwest"
    else:
        direction = "Unknown"

    st.markdown("<h1>Weather</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown(f"""
    <div style='text-align: center; font-size: 100px; line-height: 1.5;'>
        Temperature: <b>{temp}°F</b><br>
        Feels like: <b>{app_temp}°F</b><br>
        Humidity: <b>{humidity}%</b><br>
        Wind: <b>{wind_speed} mph</b> from the <b>{direction}</b><br>
        Precipitation: <b>{rain + shower}</b> inches
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.current_screen = "home"
            st.rerun()
            
    with col2:
        if st.button("📅 Daily Forecast", use_container_width=True):
            st.session_state.current_screen = "daily_weather"
            st.rerun()

elif st.session_state.current_screen == "daily_weather":
    def get_daily_weather():
        try:
            ip_api = rq.get("http://ip-api.com/json/")
            if ip_api.status_code == 200:
                ip_data = ip_api.json()
                lon = ip_data.get("lon")
                lat = ip_data.get("lat")

                daily_weather_api = rq.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,daylight_duration,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant,showers_sum,rain_sum&timezone=America%2FNew_York&forecast_days=1&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch")

                if daily_weather_api.status_code == 200:
                    weather_data = daily_weather_api.json()

                    temp_max = weather_data["daily"]["temperature_2m_max"][0]
                    temp_min = weather_data["daily"]["temperature_2m_min"][0]
                    app_temp_max = weather_data["daily"]["apparent_temperature_max"][0]
                    app_temp_min = weather_data["daily"]["apparent_temperature_min"][0]
                    raw_sunrise = weather_data["daily"]["sunrise"][0]
                    raw_sunset = weather_data["daily"]["sunset"][0]
                    uv_index = weather_data["daily"]["uv_index_max"][0]
                    daylight_seconds = weather_data["daily"]["daylight_duration"][0]
                    precipitation_probability = weather_data["daily"]["precipitation_probability_max"][0]
                    wind_speed_max = weather_data["daily"]["wind_speed_10m_max"][0]
                    main_wind_direction = weather_data["daily"]["wind_direction_10m_dominant"][0]
                    showers_sum =weather_data["daily"]["showers_sum"][0]
                    rain_sum = weather_data["daily"]["rain_sum"][0]

                    return temp_max, temp_min, app_temp_max, app_temp_min, raw_sunrise, raw_sunset, uv_index, daylight_seconds, precipitation_probability, wind_speed_max, main_wind_direction, showers_sum, rain_sum
        except Exception:
            pass
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    temp_max, temp_min, app_temp_max, app_temp_min, raw_sunrise, raw_sunset, uv_index, daylight_seconds, precipitation_probability, wind_speed_max, main_wind_direction, showers_sum, rain_sum = get_daily_weather()

    if main_wind_direction <= 22.5 or main_wind_direction > 337.5:
        direction = "north"
    elif main_wind_direction >= 22.5 and main_wind_direction < 67.5:
        direction = "northeast"
    elif main_wind_direction >= 67.5 and main_wind_direction < 112.5:
        direction = "east"
    elif main_wind_direction >= 112.5 and main_wind_direction < 157.5:
        direction = "southeast"
    elif main_wind_direction >= 157.5 and main_wind_direction < 202.5:
        direction = "south"
    elif main_wind_direction >= 202.5 and main_wind_direction < 247.5:
        direction = "southwest"
    elif main_wind_direction >= 247.5 and main_wind_direction < 292.5:
        direction = "west"
    elif main_wind_direction >= 292.5 and main_wind_direction < 337.5:
        direction = "northwest"
    else:
        direction = "Unknown"

    daylight_hours = int(daylight_seconds // 3600)
    daylight_minutes = int((daylight_seconds % 3600) // 60)

    sunrise_object = dt.datetime.strptime(raw_sunrise, "%Y-%m-%dT%H:%M")
    sunrise_time = sunrise_object.strftime("%I:%M %p")

    sunset_object = dt.datetime.strptime(raw_sunset, "%Y-%m-%dT%H:%M")
    sunset_time = sunset_object.strftime("%I:%M %p")

    st.markdown("<h1>Daily Weather</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown(f"""
    <div style='text-align: center; font-size: 100px; line-height: 1.5;'>
        Temperature: High is <b>{temp_max}°F<b/>, low is <b>{temp_min}°F<b/><br>
        Feels like: High is <b>{app_temp_max}°F<b/>, low is <b>{app_temp_min}°F<b/><br>
        Wind: <b>{wind_speed_max} mph</b> from the <b>{direction}</b><br>
        Precipitation: <b>{precipitation_probability}%<b/> chance of rain, <b>{rain_sum + showers_sum} inches</b><br>
        Total Daylight: <b>{daylight_hours}<b/> hours and <b>{daylight_minutes}<b/> minutes<br>
        UV Index: <b>{uv_index}<b/><br>
        Sunrise is at <b>{sunrise_time}<b/>, and sunset is at <b>{sunset_time}<b/>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.current_screen = "weather"
            st.rerun()
            
    with col2:
        if st.button("📅 Hourly Forecast", use_container_width=True):
            st.session_state.current_screen = "hourly_weather"
            st.rerun()

elif st.session_state.current_screen == "hourly_weather":
    def get_hourly_weather():
        try:
            ip_api = rq.get("http://ip-api.com/json/")
            if ip_api.status_code == 200:
                ip_data = ip_api.json()
                lon = ip_data.get("lon")
                lat = ip_data.get("lat")

                daily_weather_api = rq.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&timezone=auto&forecast_days=1")

                if daily_weather_api.status_code == 200:
                    weather_data = daily_weather_api.json()
                    hourly = weather_data["hourly"]

                    hourly_data = {}

                    for time_str, temp, humidity, app_temp, probability, precipitation, wind_speed, wind_direction in zip(
                        hourly["time"], 
                        hourly["temperature_2m"],
                        hourly["relative_humidity_2m"],
                        hourly["apparent_temperature"],
                        hourly["precipitation_probability"],
                        hourly["precipitation"],
                        hourly["wind_speed_10m"],
                        hourly["wind_direction_10m"],
                    ):

                        hour_label = dt.datetime.fromisoformat(time_str).strftime("%I:%M %p")
                        
                        if wind_direction <= 22.5 or wind_direction > 337.5:
                            direction = "North"
                        elif wind_direction >= 22.5 and wind_direction < 67.5:
                            direction = "Northeast"
                        elif wind_direction >= 67.5 and wind_direction < 112.5:
                            direction = "East"
                        elif wind_direction >= 112.5 and wind_direction < 157.5:
                            direction = "Southeast"
                        elif wind_direction >= 157.5 and wind_direction < 202.5:
                            direction = "South"
                        elif wind_direction >= 202.5 and wind_direction < 247.5:
                            direction = "Southwest"
                        elif wind_direction >= 247.5 and wind_direction < 292.5:
                            direction = "West"
                        elif wind_direction >= 292.5 and wind_direction < 337.5:
                            direction = "Northwest"
                        else:
                            direction = "Unknown"

                        hourly_data[hour_label] = {
                            "temp": temp,
                            "humidity": humidity,
                            "apparent_temp": app_temp,
                            "precip_prob": probability,
                            "precip_amount": precipitation,
                            "wind_speed": wind_speed,
                            "wind_direction": direction
                        }

                    return hourly_data
        except Exception:
            pass
        return {}

    hourly_weather = get_hourly_weather()

    st.markdown("<h1>Hourly Weather</h1>", unsafe_allow_html=True)
    st.write("---")
    
    for hour, data in hourly_weather.items():
        st.markdown(f"<h2>{hour}</h2>", unsafe_allow_html=True)
        st.markdown(f"""
    <div style='text-align: center; font-size: 100px; line-height: 1.5;'>
        Temperature: <b>{data['temp']}°F</b><br>
        Feels like: <b>{data['apparent_temp']}°F</b><br>
        Humidity: <b>{data['humidity']}%</b><br>
        Wind: <b>{data['wind_speed']}</b> from the <b>{data['wind_direction']}</b><br>
        Precipitation: <b>{data['precip_prob']}%</b> chance of rain, <b>{data['precip_amount']}</b> inches
    </div>
    """, unsafe_allow_html=True)
        st.write("---")

    if st.button("⬅️ Back"):
        st.session_state.current_screen = "daily_weather"
        st.rerun()
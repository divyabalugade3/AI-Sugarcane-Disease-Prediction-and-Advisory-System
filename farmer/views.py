from django.shortcuts import render, redirect
from django.conf import settings
from .models import Farmer
import requests
from datetime import datetime


def get_weather(location, village, taluka, district, state):

    # ---------- Geoapify ----------

    geo_url = (
        f"https://api.geoapify.com/v1/geocode/search?"
        f"text={location}"
        f"&filter=countrycode:in"
        f"&limit=1"
        f"&apiKey={settings.GEOAPIFY_API_KEY}"
    )

    geo = requests.get(geo_url).json()

    if not geo["features"]:
        return None

    prop = geo["features"][0]["properties"]

    lat = prop["lat"]
    lon = prop["lon"]

    village = village

    taluka = prop.get("county", taluka)
    district = prop.get("state_district", district)
    district = district.replace(" District", "")
    state = prop.get("state", state)

    # ---------- Tomorrow.io Current Weather ----------

    weather_url = (
        f"https://api.tomorrow.io/v4/weather/realtime?"
        f"location={lat},{lon}"
        f"&apikey={settings.TOMORROW_API_KEY}"
    )

    weather = requests.get(weather_url).json()

    print(weather)

    if "data" not in weather:
        return None

    values = weather["data"]["values"]

    # Weather Code Mapping

    weather_code = values.get("weatherCode")
    print("Weather Code:", weather_code)

    
    weather_map = {
    1000: "Sunny",
    1100: "Mostly Clear",
    1101: "Partly Cloudy",
    1102: "Mostly Cloudy",
    1001: "Cloudy",

    2000: "Fog",
    2100: "Light Fog",

    4000: "Light Rain",
    4001: "Rain",
    4200: "Light Rain",
    4201: "Heavy Rain",

    5000: "Snow",
    5100: "Light Snow",
    5101: "Heavy Snow",

    8000: "Thunderstorm",
}

    weather_name = weather_map.get(weather_code, "Unknown")

    # ---------- Tomorrow.io Forecast ----------

    forecast_url = (
    f"https://api.tomorrow.io/v4/weather/forecast?"
    f"location={lat},{lon}"
    f"&timesteps=1d"
    f"&fields=temperatureMax"
    f"&fields=temperatureMin"
    f"&fields=weatherCodeMax"
    f"&apikey={settings.TOMORROW_API_KEY}"
)
    forecast = requests.get(forecast_url).json()

    daily = forecast["timelines"]["daily"][:7]

    for day in daily:
        try:
            date_obj = datetime.strptime(day["time"][:10], "%Y-%m-%d")
            day["date"] = date_obj.strftime("%d-%m-%Y")
        except:
            day["date"] = day["time"][:10]

    return {

    "village": village,

    "taluka": taluka,

    "district": district,

    "state": state,

    "temp": values.get("temperature"),

    "humidity": values.get("humidity"),

    "rainfall": values.get("rainIntensity"),

    "weather": weather_name,

    "description": weather_name,

    "forecast": daily

}

# Home Page
def home(request):
    return render(request, 'home.html')


# Registration
def register(request):

    if request.method == "POST":

        name = request.POST['name']
        username = request.POST['username']
        mobile = request.POST['mobile']
        village = request.POST['village']
        password = request.POST['password']

        Farmer.objects.create(
            name=name,
            username=username,
            mobile=mobile,
            village=village,
            password=password
        )

        return redirect('login')

    return render(request, 'register.html')


# Login
def login(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = Farmer.objects.filter(
            username=username,
            password=password
        ).first()

        if user:
            # Session Create
            request.session['farmer_id'] = user.id
            return redirect('farmer_input')

        else:
            return render(request, 'login.html', {
                'error': 'Invalid Username or Password'
            })

    return render(request, 'login.html')




# Farmer Input
def farmer_input(request):

    if 'farmer_id' not in request.session:
        return redirect('login')

    weather = None

    if request.method == "POST":

        village = request.POST.get("village")
        taluka = request.POST.get("taluka")
        district = request.POST.get("district")
        state = request.POST.get("state")

        location = f"{village}, {taluka}, {district}, {state}, India"

        weather = get_weather(location, village, taluka, district, state)
        
        
        water = request.POST.get('water')
        leaf_color = request.POST.get('leaf_color')
        pest = request.POST.get('pest')

        humidity = weather["humidity"] if weather else 0
        temp = weather["temp"] if weather else 0

        disease = "Healthy Crop"
        advice = "Continue regular farming practices."

        risk = "LOW"
        probability = 20
        crop_health = 95

        nitrogen = "120 kg/ha"
        phosphorus = "60 kg/ha"
        potassium = "40 kg/ha"

        fertilizer = "Apply fertilizer in recommended quantity."

        weather_impact = "Weather conditions are favorable."
        
        advice = "Continue regular farming practices."
        disease_name = "Healthy Crop"

        if (
            water == "Yes"
            or humidity > 80
            or temp > 35
            or leaf_color == "Light Green"
            or pest == "Yes"
        ):
            disease = "⚠ Disease Risk Detected"
            disease_name = "Red Rot"

            risk = "HIGH"
            probability = 88
            crop_health = 65

            weather_impact = "High humidity and cloudy weather increase fungal disease risk."

            nitrogen = "100 kg/ha"
            phosphorus = "60 kg/ha"
            potassium = "80 kg/ha"

            fertilizer = "Avoid excess nitrogen. Apply potassium-rich fertilizer."

            if humidity > 80:
                advice = "High humidity → Fungal disease risk. Spray fungicide."
            elif temp > 35:
                advice = "High temperature → Irrigation needed."
            else:
                advice = "Check crop regularly and take preventive measures."

        return render(request, 'result.html', {
            'disease': disease,
            'advice': advice,
            'weather': weather,

            'risk': risk,
            'probability': probability,
            'crop_health': crop_health,

            'disease_name': disease_name,
            'weather_impact': weather_impact,

            'nitrogen': nitrogen,
            'phosphorus': phosphorus,
            'potassium': potassium,

            'fertilizer': fertilizer,
        })

    return render(request, 'farmer_input.html')

# Logout
def logout(request):
    request.session.flush()
    return redirect('home')
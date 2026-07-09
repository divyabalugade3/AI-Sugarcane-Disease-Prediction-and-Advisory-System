from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Farmer
import requests


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

        village = request.POST.get('village')

        weather = get_weather(village)

        water = request.POST.get('water')
        previous_disease = request.POST.get('previous_disease')
        leaf_color = request.POST.get('leaf_color')
        pest = request.POST.get('pest')

        
        humidity = weather["humidity"] if weather else 0
        temp = weather["temp"] if weather else 0

        disease = "Healthy Crop"
        advice = "Continue regular farming practices."

        # SMART AI LOGIC (improved)
        if (
            water == "Yes"
            or humidity > 80
            or temp > 35
            or leaf_color == "Light Green"
            or pest == "Yes"
        ):
            disease = "⚠ Disease Risk Detected"

            if humidity > 80:
                advice = "High humidity → Fungal disease risk. Spray fungicide."
            elif temp > 35:
                advice = "High temperature → Irrigation needed."
            else:
                advice = "Check crop regularly and take preventive measures."

        return render(request, 'result.html', {
            'disease': disease,
            'advice': advice,
            'weather': weather
        })

    return render(request, 'farmer_input.html', {
        'weather': weather
    })


def get_weather(village):

    api_key = "7ac0f0f6d235880b280ea11251e92e5a"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={village},IN&appid={api_key}&units=metric"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()

        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
        }

    return None



# Logout
def logout(request):
    request.session.flush()
    return redirect('home')
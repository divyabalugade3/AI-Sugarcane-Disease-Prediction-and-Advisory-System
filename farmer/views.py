from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Farmer


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

    # Login Check
    if 'farmer_id' not in request.session:
        return redirect('login')

    if request.method == "POST":

        water = request.POST.get('water')
        previous_disease = request.POST.get('previous_disease')
        leaf_color = request.POST.get('leaf_color')
        pest = request.POST.get('pest')
        humidity = int(request.POST.get('humidity', 0))

        disease = "Healthy Crop"
        advice = "Continue regular farming practices."

        if (
            water == "Yes"
            or humidity > 80
            or leaf_color == "Light Green"
            or pest == "Yes"
        ):
            disease = "Disease Risk Detected"
            advice = "Check crop regularly and take preventive measures."

        return render(request, 'result.html', {
            'disease': disease,
            'advice': advice
        })

    return render(request, 'farmer_input.html')


# Logout
def logout(request):
    request.session.flush()
    return redirect('home')
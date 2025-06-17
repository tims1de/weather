from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from .models import City
from .forms import CityForm
import requests


def index(request):
    key = settings.OPENWEATHER_API_KEY
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=" + key
    all_cities = []
    form = CityForm()

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']

            try:
                response = requests.get(url.format(city_name))
                weather_data = response.json()

                if response.status_code == 200 and weather_data.get('cod') == 200:
                    form.save()
                    messages.success(request, 'Город успешно добавлен!')
                else:
                    messages.error(request, 'Город не найден!')

            except requests.exceptions.RequestException as e:
                messages.error(request, f'Ошибка соединения: {str(e)}!')
            except ValueError:
                messages.error(request, 'Ошибка при обработке ответа от сервера!')

    cities = City.objects.all()

    for city in cities:
        try:
            res = requests.get(url.format(city.name)).json()
            if res['cod'] == 200:
                city_info = {
                    "city": city.name,
                    "temperature": round(res["main"]["temp"], 1),
                    "icon": res["weather"][0]["icon"],
                }
                all_cities.append(city_info)
        except:
            continue

    context = {
        "all_info": all_cities,
        "form": form
    }

    return render(request, "index.html", context)
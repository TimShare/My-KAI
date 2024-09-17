import pymorphy2
import requests

class my_weather:

    # Конструктор класса, который инициализирует начальные параметры
    def __init__(self, city_name="kazan", cords_city={"lat": 55.7887, "lon": 49.1221}):
        self.openweathermap_token = "afc12bf08d7666e923e8349647fa72a1"  # Токен для доступа к API OpenWeatherMap
        self.cords_city = cords_city  # Координаты города
        self.city_name = city_name  # Название города

    # Метод для получения описания погоды в виде словаря
    def weather_description(self):
        weather = self.get_weather_by_name()  # Получение данных о погоде по названию города
        return {
            "description": weather["weather"][0]["description"].capitalize(),  # Описание погоды
            "temp": round(weather["main"]["temp"]),  # Температура
            "feels_like": round(weather["main"]["feels_like"]),  # Ощущаемая температура
            "city": weather["name"]  # Название города
        }

    # Метод для получения данных о погоде по координатам города
    def get_weather_by_cords(self, lang="ru"):
        lat = self.cords_city["lat"]
        lon = self.cords_city["lon"]
        req_api = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.openweathermap_token}&lang={lang}"
        )
        return req_api.json()  # Возвращает JSON ответ

    # Метод для получения данных о погоде по названию города
    def get_weather_by_name(self, lang="ru"):
        req_api = requests.get(
            "http://api.openweathermap.org/data/2.5/weather",
            params={'q': f"{self.city_name}", 'units': 'metric', 'lang': 'ru', 'APPID': self.openweathermap_token}
        )
        return req_api.json()  # Возвращает JSON ответ

    # Метод для склонения названия города в нужный падеж
    def gent(self, word, gent):
        morph = pymorphy2.MorphAnalyzer()
        butyavka = morph.parse(f'{word}')[0]
        gent = butyavka.inflect({f'{gent}'})
        return gent.word.capitalize()  # Возвращает слово в нужном падеже с заглавной буквы

    # Метод для форматированного вывода данных о погоде
    def formated_print(self):
        weather_description = self.weather_description()
        return f'Погода в {self.gent(weather_description["city"], "loct")}:\n' \
               f'{weather_description["description"]}\n' \
               f'Температура: {weather_description["temp"]}°C, ощущается как: {weather_description["feels_like"]}°C'

# Тестирование класса my_weather
if __name__ == "__main__":
    weather = my_weather()
    print(weather.formated_print())


import requests
from dotenv import load_dotenv
import os
load_dotenv()


class WeatherApp:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://ng3yft2vcd.re.qweatherapi.com"

    def get_weather(self, city):
        """
        获取城市的天气信息
        """
        headers = {
            "X-QW-Api-Key": self.api_key
        }
        params = {
            "location": self.get_location_city(city)
        }
        with requests.get(
                self.base_url + "/v7/weather/now", headers=headers, params=params) as response:
            data = response.json().get("now", {})
        return data

    def get_location_city(self, location):
        """
        根据城市名称获取location code对应的
        """
        headers = {
            "X-QW-Api-Key": self.api_key
        }
        params = {
            "location": location
        }
        with requests.get(
                self.base_url+"/geo/v2/city/lookup", headers=headers, params=params) as response:
            data = response.json().get("location", [{}])[0].get("id", "")
        return data


if __name__ == "__main__":
    app = WeatherApp()
    print(app.get_weather("上海"))

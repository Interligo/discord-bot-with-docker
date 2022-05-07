import os
import requests

from load_environment import load_environment


load_environment()


class XurChecker:

    def __init__(self):
        self.message_is_sent = False
        self.url = 'https://paracausal.science/xur/current.json'
        self.destiny_api_key = os.getenv('DESTINY_API_KEY')
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.190 Safari/537.36'
        }

    def is_xur_here(self) -> bool:
        """Function checking Xur position and returns True/False."""
        response = requests.get(self.url, headers=self.headers)
        data = response.json()
        return bool(data)

    def get_xur_location(self) -> str:
        """Function returns Xur's location from json."""
        response = requests.get(self.url, headers=self.headers)
        data = response.json()

        if data is None:
            return 'Тайные люди Икоры Рей сообщают, что Посланника Девяти нет в Солнечной системе.'
        else:
            planet = data['destinationName']
            location = data['bubbleName']
            return f'Тайные люди Икоры Рей сообщают, что Зур был замечен в локации: {planet}, {location}.'

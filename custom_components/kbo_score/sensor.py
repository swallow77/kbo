import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType

SCAN_INTERVAL = timedelta(seconds=5)

def setup_platform(hass: HomeAssistantType, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    add_entities([KboScoreSensor()])

class KboScoreSensor(SensorEntity):
    def __init__(self):
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "KBO Score"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        url = "https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        scores = []
        games = soup.find_all('div', class_='score')
        for game in games:
            team1 = game.find('div', class_='team1').text.strip()
            team2 = game.find('div', class_='team2').text.strip()
            score1 = game.find('div', class_='score1').text.strip()
            score2 = game.find('div', class_='score2').text.strip()
            scores.append({
                'team1': team1, 
                'team2': team2, 
                'score1': score1, 
                'score2': score2
            })

        if scores:
            first_game = scores[0]
            self._state = f"{first_game['team1']} {first_game['score1']} - {first_game['score2']} {first_game['team2']}"
            self._attributes = first_game
        else:
            self._state = "No games found"

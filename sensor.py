
import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType

SCAN_INTERVAL = timedelta(seconds=10)

# 기본 설정
def setup_platform(
    hass: HomeAssistantType, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None
):
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
        try:
            response = requests.get(url)
            response.raise_for_status()  # 요청 실패 시 예외 발생
            soup = BeautifulSoup(response.content, 'html.parser')

            # HTML 파싱 및 점수 추출
            scores = []
            games = soup.find_all('div', class_='score')  # 각 게임 정보를 담고 있는 클래스 (이 부분은 실제 확인 필요)

            # 각 게임에 대한 정보 추출
            for game in games:
                team1 = game.find('span', class_='teamT').text.strip()  # 팀1
                team2 = game.find_all('span', class_='teamT')[1].text.strip()  # 팀2
                score1 = game.find_all('span', class_='point')[0].text.strip()  # 팀1 점수
                score2 = game.find_all('span', class_='point')[1].text.strip()  # 팀2 점수
                
                scores.append({
                    'team1': team1, 
                    'team2': team2, 
                    'score1': score1, 
                    'score2': score2
                })

            # 첫 번째 경기 정보를 상태로 설정
            if scores:
                first_game = scores[0]
                self._state = f"{first_game['team1']} {first_game['score1']} - {first_game['score2']} {first_game['team2']}"
                self._attributes = first_game
            else:
                self._state = "No games found"
                self._attributes = {}
        except requests.RequestException as e:
            self._state = "Error fetching data"
            self._attributes = {'error': str(e)}

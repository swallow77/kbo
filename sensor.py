import requests
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_SCAN_INTERVAL

class KboScoresSensor(Entity):
    """Representation of a KBO scores sensor."""

    def __init__(self, name, api_url):
        self._name = name
        self._api_url = api_url
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        response = requests.get(self._api_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        scores = []
        games = soup.select('div.score')  # 실제 소스에 맞게 선택자 수정 필요

        for game in games[:5]:
            teams = game.select('.team')  # 팀 정보 선택
            score_a = game.select('.score_a')[0].text.strip()
            score_b = game.select('.score_b')[0].text.strip()

            team_a_name = teams[0].text.strip()
            team_b_name = teams[1].text.strip()

            scores.append(f"{team_a_name} ({score_a}) : {team_b_name} ({score_b})")

        self._state = ", ".join(scores)

async def async_setup_entry(hass, entry):
    """Set up the sensor from a config entry."""
    api_url = "https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="KBO Scores",
        update_method=KboScoresSensor.async_update,
        update_interval=timedelta(seconds=CONF_SCAN_INTERVAL),
    )

    sensor = KboScoresSensor("KBO 경기 점수", api_url)
    await coordinator.async_refresh()
    return True

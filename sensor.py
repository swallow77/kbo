"""KBO Scores Sensor for Home Assistant"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging
import requests
from bs4 import BeautifulSoup
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the KBO Scores sensor platform."""

    async def async_update_data():
        """Fetch data from the KBO website."""
        try:
            return get_kbo_scores()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with KBO website: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="KBO Scores",
        update_method=async_update_data,
        update_interval=asyncio.timedelta(seconds=60),  # 1분마다 업데이트
    )

    await coordinator.async_refresh()

    entities = []
    for i in range(5):  # 5개 경기
        entities.append(KboScoreSensor(coordinator, i + 1))
    async_add_entities(entities)


class KboScoreSensor(SensorEntity):
    """Representation of a KBO Score sensor."""

    def __init__(self, coordinator, game_number):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.game_number = game_number

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"KBO Game {self.game_number}"

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return f"kbo_game_{self.game_number}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.game_number - 1]

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

def get_kbo_scores():
    url = "https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        scores = []
        for i in range(1, 6):
            home_team_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.team-name:nth-child(1)")
            away_team_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.team-name:nth-child(3)")
            home_score_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.score:nth-child(1)")
            away_score_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.score:nth-child(3)")

            home_team = home_team_element.text.strip() if home_team_element else "팀 정보 없음"
            away_team = away_team_element.text.strip() if away_team_element else "팀 정보 없음"
            home_score = home_score_element.text.strip() if home_score_element else "점수 정보 없음"
            away_score = away_score_element.text.strip() if away_score_element else "점수 정보 없음"

            scores.append(f"{home_team}({home_score}):{away_team}({away_score})")

        return scores

    except requests.exceptions.RequestException as e:
        _LOGGER.error("Error fetching KBO scores: %s", e)
        return []  # 빈 리스트 반환하여 에러 처리

"""KBO Scores Sensor for Home Assistant"""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

DOMAIN = "kbo_scores"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the KBO Scores sensor platform."""
    coordinator = KboScoresCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for i in range(5):  # 5 games
        entities.append(KboScoreSensor(coordinator, SensorEntityDescription(
            key=f"kbo_game_{i+1}",
            name=f"KBO Game {i+1}",
            icon="mdi:baseball"
        )))
    async_add_entities(entities)

class KboScoresCoordinator(DataUpdateCoordinator):
    """Coordinator to manage KBO score fetching."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="KBO Scores",
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from the KBO website."""
        async with aiohttp.ClientSession() as session:
            try:
                return await get_kbo_scores(session)
            except Exception as err:
                _LOGGER.error("Error communicating with KBO website: %s", err)
                return []

class KboScoreSensor(CoordinatorEntity, SensorEntity):
    """Representation of a KBO Score sensor."""

    def __init__(self, coordinator: KboScoresCoordinator, description: SensorEntityDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.data:
            game_index = int(self.entity_description.key.split('_')[-1]) - 1
            return self.coordinator.data[game_index] if game_index < len(self.coordinator.data) else "No data"
        return "No data"

async def get_kbo_scores(session: aiohttp.ClientSession) -> list[str]:
    url = "https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.text()

        soup = BeautifulSoup(content, 'html.parser')

        scores = []
        for i in range(1, 6):
            home_team_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.team-name:nth-child(1)")
            away_team_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.team-name:nth-child(3)")
            home_score_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.score:nth-child(1)")
            away_score_element = soup.select_one(f"#contents > div.today-game > div.live-score > div:nth-child({i}) > div.team > span.score:nth-child(3)")

            home_team = home_team_element.text.strip() if home_team_element else "No team info"
            away_team = away_team_element.text.strip() if away_team_element else "No team info"
            home_score = home_score_element.text.strip() if home_score_element else "No score"
            away_score = away_score_element.text.strip() if away_score_element else "No score"

            scores.append(f"{home_team}({home_score}):{away_team}({away_score})")

        return scores

    except aiohttp.ClientError as e:
        _LOGGER.error("Error fetching KBO scores: %s", e)
        return []  # Return an empty list to handle errors

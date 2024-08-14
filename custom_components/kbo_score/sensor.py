import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType

SCAN_INTERVAL = timedelta(minutes=30)

def fetch_kbo_data():
    url = "https://sports.news.naver.com/kbaseball/index"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")

    kboMatch = soup.find_all("div", id="_tab_box_kbo")[0]
    kboMatchItems = kboMatch.find("div", class_="hmb_list").find_all("li", class_="hmb_list_items")

    matches = []
    for item in kboMatchItems:
        leftItemBox = item.find(class_="vs_list vs_list1").find(class_="inner")
        leftScore = ''.join(leftItemBox.find("div", class_="score").stripped_strings)
        leftName = leftItemBox.find("span", class_="name").text

        rightItemBox = item.find(class_="vs_list vs_list2").find(class_="inner")
        rightScore = ''.join(rightItemBox.find("div", class_="score").stripped_strings)
        rightName = rightItemBox.find("span", class_="name").text

        match_info = {
            'left_team': leftName,
            'left_score': leftScore,
            'right_team': rightName,
            'right_score': rightScore,
        }

        matches.append(match_info)

    return matches


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
):
    async_add_entities([KboSensor()])


class KboSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "KBO Match"
        self._attr_state = None
        self._attr_extra_state_attributes = {}

    @property
    def state(self):
        return self._attr_state

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    def update(self):
        matches = fetch_kbo_data()
        if matches:
            # Example: Show first match data
            first_match = matches[0]
            self._attr_state = f"{first_match['left_team']} vs {first_match['right_team']}"
            self._attr_extra_state_attributes = {
                'left_team': first_match['left_team'],
                'left_score': first_match['left_score'],
                'right_team': first_match['right_team'],
                'right_score': first_match['right_score'],
            }

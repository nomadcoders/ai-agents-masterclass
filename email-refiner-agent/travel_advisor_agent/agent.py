from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import (
    TRAVEL_ADVISOR_DESCRIPTION,
    TRAVEL_ADVISOR_INSTRUCTION,
)
from google.adk.tools.tool_context import ToolContext

MODEL = LiteLlm(model="openai/gpt-4o")


async def get_weather(tool_context: ToolContext, location: str):
    """Get current weather information for a location."""
    # Dummy implementation - returns mock data
    return {
        "location": location,
        "temperature": "22°C",
        "condition": "Partly cloudy",
        "humidity": "65%",
        "wind": "12 km/h",
        "forecast": "Mild weather with occasional clouds expected throughout the day",
    }


async def get_exchange_rate(
    tool_context: ToolContext, from_currency: str, to_currency: str, amount: float
):
    """Get exchange rate between two currencies.
    Args should always be from_currency str, to_currency str, amount flot
    """
    # Dummy implementation - returns mock data
    mock_rates = {
        ("USD", "EUR"): 0.92,
        ("USD", "GBP"): 0.79,
        ("USD", "JPY"): 149.50,
        ("USD", "KRW"): 1325.00,
        ("EUR", "USD"): 1.09,
        ("EUR", "GBP"): 0.86,
        ("GBP", "USD"): 1.27,
        ("JPY", "USD"): 0.0067,
        ("KRW", "USD"): 0.00075,
    }

    rate = mock_rates.get((from_currency, to_currency), 1.0)
    converted_amount = amount * rate

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "exchange_rate": rate,
        "converted_amount": converted_amount,
        "timestamp": "2024-03-15 10:30:00 UTC",
    }


async def get_local_attractions(
    tool_context: ToolContext, location: str, category: str = "all"
):
    """Get popular attractions and points of interest for a location."""
    # Dummy implementation - returns mock data
    attractions = {
        "Paris": [
            {
                "name": "Eiffel Tower",
                "type": "landmark",
                "rating": 4.8,
                "description": "Iconic iron lattice tower",
            },
            {
                "name": "Louvre Museum",
                "type": "museum",
                "rating": 4.7,
                "description": "World's largest art museum",
            },
            {
                "name": "Arc de Triomphe",
                "type": "monument",
                "rating": 4.6,
                "description": "Historic triumphal arch",
            },
            {
                "name": "Notre-Dame",
                "type": "cathedral",
                "rating": 4.5,
                "description": "Medieval Catholic cathedral",
            },
            {
                "name": "Sacré-Cœur",
                "type": "basilica",
                "rating": 4.4,
                "description": "Romano-Byzantine basilica",
            },
        ],
        "Tokyo": [
            {
                "name": "Tokyo Tower",
                "type": "landmark",
                "rating": 4.5,
                "description": "Communications and observation tower",
            },
            {
                "name": "Senso-ji",
                "type": "temple",
                "rating": 4.6,
                "description": "Ancient Buddhist temple",
            },
            {
                "name": "Shibuya Crossing",
                "type": "landmark",
                "rating": 4.4,
                "description": "Busiest pedestrian crossing",
            },
            {
                "name": "Meiji Shrine",
                "type": "shrine",
                "rating": 4.7,
                "description": "Shinto shrine dedicated to Emperor Meiji",
            },
            {
                "name": "Tokyo Skytree",
                "type": "tower",
                "rating": 4.6,
                "description": "Broadcasting and observation tower",
            },
        ],
        "default": [
            {
                "name": "City Center",
                "type": "area",
                "rating": 4.2,
                "description": "Main downtown area",
            },
            {
                "name": "Historical Museum",
                "type": "museum",
                "rating": 4.3,
                "description": "Local history and culture",
            },
            {
                "name": "Central Park",
                "type": "park",
                "rating": 4.1,
                "description": "Main public park",
            },
            {
                "name": "Old Town",
                "type": "district",
                "rating": 4.4,
                "description": "Historic district with traditional architecture",
            },
            {
                "name": "Local Market",
                "type": "market",
                "rating": 4.0,
                "description": "Traditional local marketplace",
            },
        ],
    }

    location_attractions = attractions.get(location, attractions["default"])

    if category != "all":
        location_attractions = [
            a for a in location_attractions if a["type"] == category
        ]

    return {
        "location": location,
        "category": category,
        "attractions": location_attractions,
        "total_count": len(location_attractions),
    }


travel_advisor_agent = Agent(
    name="TravelAdvisorAgent",
    description=TRAVEL_ADVISOR_DESCRIPTION,
    instruction=TRAVEL_ADVISOR_INSTRUCTION,
    tools=[
        get_weather,
        get_exchange_rate,
        get_local_attractions,
    ],
    model=MODEL,
)

root_agent = travel_advisor_agent

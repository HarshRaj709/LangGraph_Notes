from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Weather Server")

@mcp.tool()
def get_temperature(city: str) -> float: 
    """Returns te temperature of city in celcius"""
    data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=9c6f1d7188a34532b8f134818261306&q={city}")
    wheather_data = data.json()
    return wheather_data["current"]["temp_c"]

if __name__ == "__main__":
    mcp.run()
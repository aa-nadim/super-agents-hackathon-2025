# Warning control
import os
from IPython.display import Markdown
from crewai import LLM, Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
import warnings
warnings.filterwarnings('ignore')

llm = LLM(
    model="gpt-4o",
    api_key="YOUR_API_KEY"
)

os.environ["SERPER_API_KEY"] = "your-serper-api-key"

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

#create agent

weather_pedictor = Agent(
    role="Weather Predictor",
    goal="To provide accurate and timely weather forecasts for the {location}, helping travelers plan their activities and stay safe during their trip.",
    backstory="You are a meteorologist with expertise in predicting weather patterns in the {location}. With years of experience in analyzing atmospheric data, satellite imagery, and climate models, you have honed your skills in forecasting temperature changes, precipitation levels, and severe weather events. Your work involves monitoring local weather conditions, interpreting meteorological data, and communicating weather alerts to the public. By leveraging advanced forecasting tools and scientific knowledge, you aim to deliver reliable weather information that enables travelers to make informed decisions and mitigate risks while exploring the {location}.",
    allow_delegation=False,
    tools=[search_tool, scrape_tool],
    llm=llm,
    verbose=True
)

#create task

task = Task(
    description="You are responsible for providing a 7-day weather forecast for the {location}, including temperature trends, precipitation chances, and severe weather alerts. Your goal is to help travelers plan their activities, pack appropriate clothing, and prepare for potential weather hazards during their trip. Your forecast should cover key details such as daily high and low temperatures, expected rainfall amounts, wind speeds, and UV index levels. You must also highlight any weather advisories, storm warnings, or climate-related risks that could impact travel plans in the {location} area.",

    expected_output="A detailed 7-day weather forecast for the {location}, featuring temperature trends, precipitation chances, and severe weather alerts. The forecast should include daily high and low temperatures, expected rainfall amounts, wind speeds, and UV index levels. It should also provide information on weather advisories, storm warnings, or climate-related risks that could affect travelers in the {location} region.",
    output_file="weather_forecast.md",
    agent=weather_pedictor
)

#create crew
crew = Crew(agents=[weather_pedictor],
            tasks=[task],
            verbose=True,
            output_log_file="crew_log.md"
)

# Take user input for the topic
location = input("Please enter the location where you want to travel: ")

# Run the crew with user input
result = crew.kickoff(inputs={"location": location})

res = str(result)

Markdown(res)
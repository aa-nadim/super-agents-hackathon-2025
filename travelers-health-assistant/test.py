from flask import Flask, render_template, request
from crewai import LLM, Agent, Task, Crew
from crewai_tools import SerperDevTool
import warnings
import os
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings('ignore')

OPEN_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

app = Flask(__name__)

# Set up the LLM, API keys, and agents
llm = LLM(
    model="gpt-4",
    api_key=OPEN_API_KEY,
)

os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()

# Create agents
weather_agent = Agent(
    role='Weather Analyst',
    goal='Accurately predict and analyze weather conditions for the specified location',
    backstory="""You are an experienced meteorologist with expertise in weather analysis 
    and forecasting. Your job is to provide accurate weather information to help travelers 
    plan their trips safely.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

safety_agent = Agent(
    role='Safety Advisor',
    goal='Provide safety precautions based on weather conditions',
    backstory="""You are a travel safety expert with deep knowledge of how weather 
    conditions affect travel safety. You provide crucial safety advice to ensure 
    travelers are well-prepared.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

tour_planner = Agent(
    role='Tour Planner',
    goal='Create optimal tour plans considering weather conditions',
    backstory="""You are an experienced tour planner who specializes in creating 
    adaptable travel itineraries based on weather conditions and location-specific 
    attractions.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

medical_advisor = Agent(
    role='Medical Advisor',
    goal='Identify potential medical risks and provide preventive advice',
    backstory="""You are a travel medicine specialist who helps travelers understand 
    and prepare for potential medical issues they might face during their journey.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

emergency_locator = Agent(
    role='Emergency Services Locator',
    goal='Provide information about local emergency services and medical facilities',
    backstory="""You are a local emergency services expert who maintains updated 
    information about medical facilities and emergency contacts in various locations.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

def create_tasks(location):
    tasks = [
        Task(
            description=f"Analyze and predict the current and upcoming weather conditions for {location}. Include temperature, precipitation, and any weather warnings.",
            agent=weather_agent,
            expected_output="Detailed weather analysis and forecast for the specified location"
        ),
        Task(
            description=f"Based on the weather analysis for {location}, provide detailed safety precautions and recommendations for travelers. Include what to pack and what to avoid.",
            agent=safety_agent,
            expected_output="Comprehensive safety recommendations based on weather conditions"
        ),
        Task(
            description=f"Create a flexible tour plan for {location} considering the weather conditions. Include indoor and outdoor activities with alternatives for bad weather.",
            agent=tour_planner,
            expected_output="Detailed tour plan with weather-appropriate activities"
        ),
        Task(
            description=f"Identify potential medical conditions and health risks travelers might face in {location}. Provide preventive measures and recommendations.",
            agent=medical_advisor,
            expected_output="List of medical risks and preventive measures"
        ),
        Task(
            description=f"""Compile a list of emergency services in {location}, including:
            - Hospitals and their specialties
            - 24/7 pharmacies
            - Emergency contact numbers
            - Medical facilities' addresses""",
            agent=emergency_locator,
            expected_output="Comprehensive list of emergency services and contacts"
        )
    ]
    return tasks

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        location = request.form['location']
        
        try:
            # Create tasks with the specific location
            tasks = create_tasks(location)
            
            # Create crew with the new tasks
            crew = Crew(
                agents=[weather_agent, safety_agent, tour_planner,
                       medical_advisor, emergency_locator],
                tasks=tasks
            )
            
            # Execute all tasks and get the raw result
            results_raw = crew.kickoff()
            
            # Convert the results to a list if it's not already
            if not isinstance(results_raw, list):
                results_raw = [results_raw]
            
            # Create results list with titles
            section_titles = [
                'Weather Analysis',
                'Safety Precautions',
                'Tour Plan',
                'Medical Risks',
                'Emergency Services'
            ]
            
            # Combine titles with content
            results = [
                {'title': title, 'content': str(content)}
                for title, content in zip(section_titles, results_raw)
            ]
            
        except Exception as e:
            # Handle any errors
            results = [{
                'title': 'Error',
                'content': f"An error occurred while processing your request: {str(e)}"
            }]
        
        return render_template('index.html', results=results)

    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
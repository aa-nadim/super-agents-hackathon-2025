from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# Initialize the search tool
search_tool = SerperDevTool()

# Create the Weather Agent
weather_agent = Agent(
    role='Weather Analyst',
    goal='Accurately predict and analyze weather conditions for the specified location',
    backstory="""You are an experienced meteorologist with expertise in weather analysis 
    and forecasting. Your job is to provide accurate weather information to help travelers 
    plan their trips safely.""",
    tools=[search_tool],
    verbose=True
)

# Create the Safety Advisor Agent
safety_agent = Agent(
    role='Safety Advisor',
    goal='Provide safety precautions based on weather conditions',
    backstory="""You are a travel safety expert with deep knowledge of how weather 
    conditions affect travel safety. You provide crucial safety advice to ensure 
    travelers are well-prepared.""",
    tools=[search_tool],
    verbose=True
)

# Create the Tour Planner Agent
tour_planner = Agent(
    role='Tour Planner',
    goal='Create optimal tour plans considering weather conditions',
    backstory="""You are an experienced tour planner who specializes in creating 
    adaptable travel itineraries based on weather conditions and location-specific 
    attractions.""",
    tools=[search_tool],
    verbose=True
)

# Create the Medical Advisor Agent
medical_advisor = Agent(
    role='Medical Advisor',
    goal='Identify potential medical risks and provide preventive advice',
    backstory="""You are a travel medicine specialist who helps travelers understand 
    and prepare for potential medical issues they might face during their journey.""",
    tools=[search_tool],
    verbose=True
)

# Create the Emergency Services Locator Agent
emergency_locator = Agent(
    role='Emergency Services Locator',
    goal='Provide information about local emergency services and medical facilities',
    backstory="""You are a local emergency services expert who maintains updated 
    information about medical facilities and emergency contacts in various locations.""",
    tools=[search_tool],
    verbose=True
)

def create_travel_crew(location):
    # Task 1: Weather Analysis
    weather_task = Task(
        description=f"""Analyze and predict the current and upcoming weather conditions for {location}.
        Include temperature, precipitation, and any weather warnings.""",
        agent=weather_agent
    )

    # Task 2: Safety Precautions
    safety_task = Task(
        description=f"""Based on the weather analysis for {location}, provide detailed safety 
        precautions and recommendations for travelers. Include what to pack and what to avoid.""",
        agent=safety_agent
    )

    # Task 3: Tour Planning
    planning_task = Task(
        description=f"""Create a flexible tour plan for {location} considering the weather 
        conditions. Include indoor and outdoor activities with alternatives for bad weather.""",
        agent=tour_planner
    )

    # Task 4: Medical Risk Assessment
    medical_task = Task(
        description=f"""Identify potential medical conditions and health risks travelers 
        might face in {location}. Provide preventive measures and recommendations.""",
        agent=medical_advisor
    )

    # Task 5: Emergency Services Information
    emergency_task = Task(
        description=f"""Compile a list of emergency services in {location}, including:
        - Hospitals and their specialties
        - 24/7 pharmacies
        - Emergency contact numbers
        - Medical facilities' addresses""",
        agent=emergency_locator
    )

    # Create the crew
    crew = Crew(
        agents=[weather_agent, safety_agent, tour_planner, medical_advisor, emergency_locator],
        tasks=[weather_task, safety_task, planning_task, medical_task, emergency_task],
        verbose=2
    )

    return crew

def main():
    # Get location input from user
    location = input("Enter the location you want to travel to: ")
    
    # Create and kick off the crew
    crew = create_travel_crew(location)
    result = crew.kickoff()
    
    # Process and display results
    print("\n=== Travel Assistant Report ===")
    print(result)

if __name__ == "__main__":
    main()
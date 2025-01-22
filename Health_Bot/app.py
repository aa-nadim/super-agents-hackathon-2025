import os
from flask import Flask, jsonify, render_template, request, Response, stream_with_context
from crewai import LLM, Agent, Task, Crew
from crewai_tools import SerperDevTool
import warnings
import json
from functools import partial

# Initialize Flask app
app = Flask(__name__)

# Setup for warnings and tools
warnings.filterwarnings('ignore')

# Initialize LLM and other tools
llm = LLM(
    model="gpt-4o",
    api_key=""
)

os.environ["SERPER_API_KEY"] = ""

search_tool = SerperDevTool()

# Define agents (same as before)
weather_agent = Agent(
    role='Weather Analyst',
    goal='Accurately predict and analyze weather conditions for the specified location',
    backstory="""You are an experienced meteorologist with expertise in weather analysis and forecasting.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

safety_agent = Agent(
    role='Safety Advisor',
    goal='Provide safety precautions based on weather conditions',
    backstory="""You are a travel safety expert with deep knowledge of how weather conditions affect travel safety.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

tour_planner = Agent(
    role='Tour Planner',
    goal='Create optimal tour plans considering weather conditions',
    backstory="""You are an experienced tour planner who specializes in creating adaptable travel itineraries.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

medical_advisor = Agent(
    role='Medical Advisor',
    goal='Identify potential medical risks and provide preventive advice',
    backstory="""You are a travel medicine specialist who helps travelers understand potential medical issues.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

emergency_locator = Agent(
    role='Emergency Services Locator',
    goal='Provide information about local emergency services and medical facilities',
    backstory="""You are a local emergency services expert with knowledge of medical facilities.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

insurance_advisor = Agent(
    role='Insurance Advisor',
    goal='Assess travel insurance needs and provide recommendations',
    backstory="""You are an insurance advisor specializing in travel and health insurance.""",
    tools=[search_tool],
    verbose=True,
    llm=llm
)

def create_task(description, agent, expected_output, context=None):
    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output,
        context=context if context else []
    )

def process_task(task, location):
    """Process a single task and return its result"""
    crew = Crew(
        agents=[task.agent],
        tasks=[task]
    )
    result = crew.kickoff(inputs={"location": location})
    return {
        "agent": task.agent.role,
        "result": str(result)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_travel_advisory')
def get_travel_advisory():
    def generate():
        try:
            location = request.args.get('location')
            if not location:
                yield f"data: {json.dumps({'error': 'Location is required'})}\n\n"
                return
            
            # Create tasks
            tasks = [
                create_task(
                    f"Analyze current and upcoming weather conditions for {location}.",
                    weather_agent,
                    "Weather analysis and forecasts"
                ),
                create_task(
                    f"Provide safety precautions for {location} travelers.",
                    safety_agent,
                    "Safety recommendations"
                ),
                create_task(
                    f"Create a flexible tour plan for {location}.",
                    tour_planner,
                    "Tour itinerary"
                ),
                create_task(
                    f"Identify medical risks in {location}.",
                    medical_advisor,
                    "Medical risk assessment"
                ),
                create_task(
                    f"Compile emergency services list for {location}.",
                    emergency_locator,
                    "Emergency services list"
                ),
                create_task(
                    f"Provide insurance recommendations for {location}.",
                    insurance_advisor,
                    "Insurance recommendations"
                )
            ]
            
            # Process each task and stream results
            for task in tasks:
                result = process_task(task, location)
                yield f"data: {json.dumps(result)}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
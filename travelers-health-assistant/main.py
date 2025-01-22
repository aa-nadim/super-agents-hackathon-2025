import os
from flask import Flask, jsonify, render_template, request, Response, stream_with_context
from crewai import LLM, Agent, Task, Crew
from crewai_tools import SerperDevTool
import warnings
import json
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache
import concurrent.futures

# Initialize Flask app
app = Flask(__name__)

# Setup for warnings and tools
warnings.filterwarnings('ignore')

# Cache for storing results with a 1-hour TTL
results_cache = TTLCache(maxsize=100, ttl=3600)

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=3)
# Initialize LLM and other tools
llm = LLM(
    model="gpt-4o",
    api_key=""
)

os.environ["SERPER_API_KEY"] = ""
search_tool = SerperDevTool()

# Define all agents
def create_shared_agents():
    return {
        'weather': Agent(
            role='Weather Analyst',
            goal='Accurately predict and analyze weather conditions',
            backstory="You are an experienced meteorologist with expertise in weather analysis and forecasting.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        ),
        'safety': Agent(
            role='Safety Advisor',
            goal='Provide safety precautions based on weather conditions',
            backstory="You are a travel safety expert with deep knowledge of weather impacts.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        ),
        'tour': Agent(
            role='Tour Planner',
            goal='Create optimal tour plans considering weather conditions',
            backstory="You are an experienced tour planner who specializes in creating adaptable travel itineraries.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        ),
        'medical': Agent(
            role='Medical Advisor',
            goal='Identify potential medical risks and provide preventive advice',
            backstory="You are a travel medicine specialist who helps travelers understand potential medical issues.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        ),
        'emergency': Agent(
            role='Emergency Services Locator',
            goal='Provide information about local emergency services and medical facilities',
            backstory="You are a local emergency services expert with knowledge of medical facilities.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        ),
        'insurance': Agent(
            role='Insurance Advisor',
            goal='Assess travel insurance needs and provide recommendations',
            backstory="You are an insurance advisor specializing in travel and health insurance.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        ),
        'supervisor': Agent(
            role='Travel Advisory Supervisor',
            goal='Compile and organize all travel advisory information into a comprehensive report',
            backstory="You are a senior travel advisor who specializes in creating comprehensive travel reports.",
            tools=[search_tool],
            verbose=False,
            llm=llm
        )
    }

# Create shared agents
shared_agents = create_shared_agents()

def get_cached_result(location, agent_role):
    """Get cached result for a location and agent role"""
    cache_key = f"{location}_{agent_role}"
    return results_cache.get(cache_key)

def set_cached_result(location, agent_role, result):
    """Set cached result for a location and agent role"""
    cache_key = f"{location}_{agent_role}"
    results_cache[cache_key] = result

def process_task(task, location, previous_results=None):
    """Process a single task synchronously"""
    # Check cache first
    cached_result = get_cached_result(location, task.agent.role)
    if cached_result and task.agent.role != 'supervisor':  # Don't use cache for supervisor
        return {
            "agent": task.agent.role,
            "result": cached_result
        }

    # Process task if not cached
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process_timeout=60
    )
    
    # Add previous results to inputs if this is the supervisor task
    inputs = {"location": location}
    if previous_results is not None:
        inputs["previous_results"] = previous_results
    
    result = crew.kickoff(inputs=inputs)
    
    # Cache the result (except for supervisor)
    if task.agent.role != 'supervisor':
        set_cached_result(location, task.agent.role, str(result))
    
    return {
        "agent": task.agent.role,
        "result": str(result)
    }

def create_task(description, agent, expected_output, context=None):
    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output,
        context=context if context else []
    )

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

            # Create initial tasks with shared agents
            initial_tasks = [
                create_task(
                    f"Analyze current and upcoming weather conditions for {location}.",
                    shared_agents['weather'],
                    "Weather analysis and forecasts"
                ),
                create_task(
                    f"Provide safety precautions for {location} travelers.",
                    shared_agents['safety'],
                    "Safety recommendations"
                ),
                create_task(
                    f"Create a flexible tour plan for {location}.",
                    shared_agents['tour'],
                    "Tour itinerary"
                ),
                create_task(
                    f"Identify medical risks in {location}.",
                    shared_agents['medical'],
                    "Medical risk assessment"
                ),
                create_task(
                    f"Compile emergency services list for {location}.",
                    shared_agents['emergency'],
                    "Emergency services list"
                ),
                create_task(
                    f"Provide insurance recommendations for {location}.",
                    shared_agents['insurance'],
                    "Insurance recommendations"
                )
            ]

            all_results = []

            # Process initial tasks using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_task = {executor.submit(process_task, task, location): task for task in initial_tasks}
                
                for future in concurrent.futures.as_completed(future_to_task):
                    try:
                        result = future.result()
                        all_results.append(result)
                        yield f"data: {json.dumps(result)}\n\n"
                    except Exception as e:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

            # Create and process supervisor task after all other tasks are complete
            supervisor_task = create_task(
                f"""Create a comprehensive travel advisory report for {location} by organizing and summarizing the following information:
                {json.dumps(all_results, indent=2)}
                
                Format the report with clear sections for:
                - Executive Summary
                - Weather Analysis
                - Safety Precautions
                - Tour Planning
                - Medical Risks and Services
                - Emergency Services
                - Insurance Recommendations
                
                Format the output in a clear, well-structured manner using Markdown.""",
                shared_agents['supervisor'],
                "Complete travel advisory report"
            )

            supervisor_result = process_task(supervisor_task, location, all_results)
            yield f"data: {json.dumps(supervisor_result)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, threaded=True)
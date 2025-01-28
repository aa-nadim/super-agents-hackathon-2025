from crewai import Agent, Task, Crew, LLM

# Initialize LLM
llm = LLM(
    model="gpt-4o",
    base_url="https://openai.prod.ai-gateway.quantumblack.com/0b0e19f0-3019-4d9e-bc36-1bd53ed23dc2/v1",
    api_key="5f393389-5fc3-4904-a597-dd56e3b00f42:7ggTi5OqYeCqlLm1PmJ9kkAVk69iWuWI"
)

# Define the HTML/CSS Generator Agent
html_css_agent = Agent(
    role='HTML/CSS Developer',
    goal='Generate clean and responsive HTML/CSS code based on user requirements',
    backstory='You are a skilled front-end developer who specializes in creating modern, responsive, and accessible web components.',
    tools=[],
    llm=llm
)

# Take user input for the component type
component_type = input("Enter the type of component you want to generate (e.g., 'Feature-left-section', 'Navbar', 'Footer'): ")

# Define the Task for Generating HTML/CSS Code based on user input
generate_html_css_task = Task(
    description=f'Generate a responsive HTML/CSS component for a {component_type} layout.',
    expected_output='A clean and responsive HTML/CSS code for the specified component. Only the HTML/CSS code is required in proper HTML5 format, no extra text or format. Without any html markdown syntax',
    agent=html_css_agent,
    output_file=f'output/{component_type.lower().replace(" ", "_")}_component.html'  # Save the generated code to a HTML file
)

# Create the Crew and Execute the Task
crew = Crew(
    agents=[html_css_agent],
    tasks=[generate_html_css_task]
)

# Execute the Crew
result = crew.kickoff()

# Output the Generated HTML/CSS Code
print(f"Generation completed. Check the output file: "
    f"output/{component_type.lower().replace(" ", "_")}_component.html")
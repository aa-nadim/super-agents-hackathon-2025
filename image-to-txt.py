from crewai import Agent, Task, Crew, LLM

# Initialize LLM
llm = LLM(
    model="gpt-4o",
    base_url="https://openai.prod.ai-gateway.quantumblack.com/0b0e19f0-3019-4d9e-bc36-1bd53ed23dc2/v1",
    api_key="5f393389-5fc3-4904-a597-dd56e3b00f42:7ggTi5OqYeCqlLm1PmJ9kkAVk69iWuWI"
)

# Create a multimodal agent
image_analyst = Agent(
    role="Product Analyst",
    goal="Analyze product images and provide detailed descriptions",
    backstory="Expert in visual product analysis with deep knowledge of design and features",
    llm=llm,
    multimodal=True
)

# Take user input for the component type
image_link = input("Enter the image link you want to analysis: ")

# Create a task for image analysis
task = Task(
    description=f"Analyze the product image at {image_link} and provide a detailed description",
    agent=image_analyst,
    verbose=True,
    output_file="outputs/vrbo2.md",
    expected_output="A detailed written description of the product based on visual analysis"
)

# Create and run the crew
crew = Crew(
    agents=[image_analyst],
    tasks=[task]
)

result = crew.kickoff()

# Output the Generated HTML/CSS Code
print(f"Generation completed. Check the output file for the generated details analysis for {image_link}.")
# Warning control
from IPython.display import Markdown
from crewai import LLM, Agent, Task, Crew
import warnings
warnings.filterwarnings('ignore')


# llm = LLM(
#     model="ollama/llama3.2",
#     base_url="http://localhost:11434"
# )


llm = LLM(
model="gpt-4o",
api_key="your-api-key"
)

#create planner agent
planner = Agent(
    role="Tropical Health Advisor",
    goal="To provide comprehensive, up-to-date health and food safety guidance for travelers planning to explore the {location}, ensuring their well-being and safety during the trip.",
    backstory="You are an expert in tropical diseases, environmental health, and food safety, with years of experience working in {location}. They have an extensive background in advising travelers, ecotourists, and field researchers on how to minimize health risks while navigating through dense, remote environments. Having worked with local health organizations and international travel agencies, the advisor is highly knowledgeable about regional risks, preventive measures, and available medical resources. They understand both the physical challenges of the {location} and the cultural nuances of local food safety practices, ensuring travelers have the information they need to stay healthy and make informed choices while enjoying their adventure in one of the most biodiverse ecosystems in the world.",
    allow_delegation=False,
    llm=llm,
	verbose=True
)

#create task

task = Task(
    description="You are planning a trip to the {location} and need to prepare a detailed health and food safety guide for travelers. Your goal is to provide comprehensive advice on how to prevent common tropical diseases, avoid foodborne illnesses, and stay safe in the {location} environment. Your guide should cover essential topics such as vaccination recommendations, insect bite prevention, water purification methods, and safe food handling practices. You must also include emergency contact information, local healthcare facilities, and tips for managing health issues while traveling in remote areas. Your target audience includes adventure seekers, nature enthusiasts, and researchers planning to explore the {location} for the first time.",

    expected_output="A detailed health and food safety guide for travelers planning a trip to the {location}. The guide should include information on common tropical diseases, vaccination recommendations, insect bite prevention, water purification methods, safe food handling practices, emergency contact information, local healthcare facilities, and tips for managing health issues in remote areas. The content should be informative, practical, and tailored to the needs of travelers exploring the {location} environment.",

    output_file="health_safety_guide.md",
    agent=planner
)

#create crew
crew = Crew(agents=[planner],
            tasks=[task],
            varbose=True,
            output_log_file="crew_log.md"
)

# Take user input for the topic
location = input("Please enter the location where you want to travel: ")

# Run the crew with user input
result = crew.kickoff(inputs={"location": location})

res = str(result)
Markdown(res)
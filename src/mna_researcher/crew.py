from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os

#####################################

from crewai.tools import tool

from news_search_client import NewsSearchClient
from azure.core.credentials import AzureKeyCredential
SUBSCRIPTION_KEY = os.getenv("BING_SEARCH_SUBSCRIPTION_KEY")
ENDPOINT = "https://api.bing.microsoft.com" + "/v7.0/"

def news_search(param_query):
    """NewsSearch using BING API, latest 4 news description for the given query.
    """
    client = NewsSearchClient(
        endpoint=ENDPOINT, credential=AzureKeyCredential(SUBSCRIPTION_KEY)
    )

    try:
        news_result = client.news.search(
            query=param_query, market="en-us", count=2, freshness="Month",
        )
        if news_result.value:
            return [n.description for n in news_result.value]

    except Exception as err:
        return []
	
@tool("MyCustomSearchTool")
def MyCustomSearchTool(param_topic: str) -> str:
    """ Search a Topic in Bing News API"""
    print("News API called")
    # Tool logic here
    return news_search(param_topic)


#####################################

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class MnaResearcher():
	"""MnaResearcher crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[MyCustomSearchTool],
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.html'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the MnaResearcher crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

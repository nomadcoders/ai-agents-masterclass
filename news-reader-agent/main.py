import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew


@CrewBase
class NewsReaderAgent:

    @agent
    def news_hunter_agent(self):
        return Agent(
            config=self.agents_config["news_hunter_agent"],
        )

    @agent
    def summarizer_agent(self):
        return Agent(
            config=self.agents_config["summarizer_agent"],
        )

    @agent
    def curator_agent(self):
        return Agent(
            config=self.agents_config["curator_agent"],
        )

    @task
    def content_harvesting_task(self):
        return Task(
            config=self.tasks_config["content_harvesting_task"],
        )

    @task
    def summarization_task(self):
        return Task(
            config=self.tasks_config["summarization_task"],
        )

    @task
    def final_report_assembly_task(self):
        return Task(
            config=self.tasks_config["final_report_assembly_task"],
        )

    @crew
    def crew(self):
        return Crew(
            tasks=self.tasks,
            agents=self.agents,
            verbose=True,
        )


NewsReaderAgent().crew().kickoff()

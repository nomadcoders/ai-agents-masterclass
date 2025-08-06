from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Task, Crew
from pydantic import BaseModel


class Score(BaseModel):
    score: int
    reason: str


@CrewBase
class ViralityCrew:

    @agent
    def virality_expert(self):
        return Agent(
            role="Social Media Virality Expert",
            goal="Analyze social media content for viral potential and provide a score with actionable feedback",
            backstory="""You are a social media strategist with deep expertise in viral content creation. 
            You've analyzed thousands of viral posts across Twitter and LinkedIn, understanding the psychology 
            of engagement, shareability, and what makes content spread. You know the specific mechanics that 
            drive virality on each platform - from hook writing to emotional triggers.""",
            verbose=True,
        )

    @task
    def virality_audit(self):
        return Task(
            description="""Analyze the social media content for viral potential and provide:
            
            1. A virality score from 0-10 based on:
               - Hook strength and attention-grabbing potential
               - Emotional resonance and relatability
               - Shareability factor
               - Call-to-action effectiveness
               - Platform-specific best practices
               - Trending topic alignment
               - Content format optimization
               
            2. A clear reason explaining the score, focusing on:
               - What makes this content likely to go viral (if score is high)
               - Critical elements missing for virality (if score is low)
               - The single most important improvement needed
            
            Content to analyze: {content}
            Content type: {content_type}
            Target topic: {topic}
            """,
            expected_output="""A Score object with:
            - score: integer from 0-10 rating the viral potential
            - reason: string explaining the main factors affecting virality""",
            agent=self.virality_expert(),
            output_pydantic=Score,
        )

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )

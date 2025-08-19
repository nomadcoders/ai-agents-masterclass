from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from agents import Runner
import streamlit as st


class CustomWorkflow(VoiceWorkflowBase):

    def __init__(self, context):

        self.context = context

    async def run(self, transcription):

        result = Runner.run_streamed(
            st.session_state["agent"],
            transcription,
            session=st.session_state["session"],
            context=self.context,
        )

        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk

        st.session_state["agent"] = result.last_agent

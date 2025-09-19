from pydantic import BaseModel
from agents import Agent, Runner
from dotenv import load_dotenv
import asyncio
from langchain.tools import Tool

from functions.query_database import query_rag
from functions.helper import read_instructions, parse_failure_modes_to_dataframe

from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
import streamlit as st
import os
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import pandas as pd
import json

# Load environment variables
load_dotenv(find_dotenv())

# os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']


# Planner Agent
class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class FailureMode(BaseModel):
    id: str = Field(description="Unique identifier")
    failure_mode: str = Field(description="Failure mode name")
    failure_cause: str = Field(description="Failure cause")
    failure_effect: str = Field(description="Failure effect")
    mitigation: Optional[str] = Field(description="Suggested mitigation")
    # severity: Severity
    # impact: str = Field(description="Impact description")
    # priority: int = Field(ge=1, le=10, description="Priority 1-10")

class FailureModeResponse(BaseModel):
    failure_modes: List[FailureMode]
    # total_count: int
    # high_priority_items: int
    # summary: str


fm_instruction= read_instructions("roger.md") + read_instructions("failure_mode.md")
fm_agent = Agent(
    name="Failure Mode Checker Agent",
    instructions=fm_instruction,
    output_type=FailureModeResponse
)
# manual_instruction= read_instructions("roger.md") + read_instructions("manual.md")
# manual_agent = Agent(
#     name="Manual Checker Agent",
#     instructions=manual_instruction

async def main():
    #
    st.set_page_config(page_title="Failure Mode And Effect Analysis Tool")
    st.image("media/engineer.png")
    st.header("Failure Mode And Effect Analysis Tool")

    # Clear all cached data
    st.cache_data.clear()
    st.cache_resource.clear()

    # Initialize session state for history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

    # os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    # query_text = "How to change a tire?"
    # query_text = st.text_input("Enter the equipment:", placeholder="Enter the equipment")

    # equipment = st.radio(
    #     "Which equipment would you like to check?",
    #     ["Electric Motor", "Seals and Gaskets", "Pumps"])

    equipment = st.selectbox(
        "Which equipment would you like to generate a FMEA sheet?",
        ["Electric Motor", "Seals and Gaskets", "Pumps", "Valves", "Bearings", "Compressors", "Actuators"])

    # Submit button
    if st.button("Submit"):
        if equipment:
            with st.spinner("Processing..."):
                
                request, sources = query_rag(equipment, os.environ['OPENAI_API_KEY'])
                print(equipment)
                print(request)

                # run planner agent
                result = await Runner.run(
                    fm_agent,
                    request
                )
                st.write(f"FMEA for {equipment}")
            # st.write(result.final_output)
            # st.write(sources)
            # print(result.final_output)
            # print(sources)

            # Extract the failure_modes array
            df = parse_failure_modes_to_dataframe(result.final_output)
            for col in df.select_dtypes(include='object').columns:
                df[col] = df[col].astype(str)
            # st.dataframe(df)

            with st.container():
                st.markdown("""
                <style>
                .stTable {
                    width: 100%;
                }
                table {
                    width: 100% !important;
                    min-width: 600px;
                    max-width: 1200px;
                }
                /* Set specific widths for each column */
                table th:nth-child(1), table td:nth-child(1) { width: 4%; }  /* Column 1 */
                table th:nth-child(2), table td:nth-child(2) { width: 6%; }  /* Column 2 */
                table th:nth-child(3), table td:nth-child(3) { width: 15%; }  /* Column 3 */
                table th:nth-child(4), table td:nth-child(4) { width: 25%; }  /* Column 4 */
                table th:nth-child(5), table td:nth-child(5) { width: 25%; }  /* Column 5 */
                table th:nth-child(6), table td:nth-child(5) { width: 25%; }  /* Column 6 */
                
                table th, table td {
                    word-wrap: break-word;
                    white-space: normal;
                    padding: 8px;
                }
                </style>
                """, unsafe_allow_html=True)

                st.table(df)

            st.write("References:")
            st.json(sources)


        else:
            st.warning("Please enter some text!")

if __name__ == "__main__":
    asyncio.run(main())
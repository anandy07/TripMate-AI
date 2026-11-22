
import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="TripMate AI",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ TripMate AI")
st.write("Your AI-powered travel planner.")

st.divider()

thread_id = "tripmate_user"

user_query = st.text_area(
    "Where do you want to travel?",
    placeholder="Example: Plan a 7-day trip from India to USA...",
    height=120
)

if st.button("Generate Travel Plan", use_container_width=True):

    if not user_query.strip():
        st.warning("Please enter your travel request.")

    else:
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        collected = {
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "final_response": "",
            "llm_calls": 0
        }

        with st.spinner("Planning your trip..."):

            for chunk in app.stream(
                {
                    "messages": [HumanMessage(content=user_query)],
                    "user_query": user_query,
                    "flight_results": "",
                    "hotel_results": "",
                    "itinerary": "",
                    "llm_calls": 0,
                },
                config=config,
                stream_mode="updates"
            ):

                for node_name, state_update in chunk.items():

                    if node_name == "flight_agent":
                        collected["flight_results"] = state_update.get(
                            "flight_results", ""
                        )

                    elif node_name == "hotel_agent":
                        collected["hotel_results"] = state_update.get(
                            "hotel_results", ""
                        )

                    elif node_name == "itinerary_agent":
                        collected["itinerary"] = state_update.get(
                            "itinerary", ""
                        )

                    elif node_name == "final_agent":
                        msgs = state_update.get("messages", [])

                        if msgs:
                            collected["final_response"] = msgs[-1].content

                    collected["llm_calls"] = state_update.get(
                        "llm_calls",
                        collected["llm_calls"]
                    )

        st.success("Travel plan generated!")

        st.subheader("Your Travel Plan")

        if collected["final_response"]:
            st.markdown(collected["final_response"])
        else:
            st.warning("No final response was generated.")

        # Download travel plan

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"

        file_content = f"""# TripMate AI - Travel Plan

**Travel Request:** {user_query}

## Flight Information
{collected['flight_results']}

## Hotel Information
{collected['hotel_results']}

## Itinerary
{collected['itinerary']}

## Final Travel Plan
{collected['final_response']}

## LLM Calls
{collected['llm_calls']}
"""

        st.download_button(
            label="Download Travel Plan",
            data=file_content,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True
        )

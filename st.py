import streamlit as st
import os
from modules.groq_client import GroqClient
from modules.serper_client import SerperClient
from modules.relevancyAgent import RelevancyAgent

# Streamlit App
st.title("Web Hunting Copilot 🔍")
st.markdown("Analyze brand presence and relevancy with ease.")

# Session State Initialization
if "queries" not in st.session_state:
    st.session_state["queries"] = []
if "processed_results" not in st.session_state:
    st.session_state["processed_results"] = []
if "relevant_results" not in st.session_state:
    st.session_state["relevant_results"] = []

# Input Section
brand_name = st.text_input("Enter Brand Name:", placeholder="e.g., OpenAI, Netflix, PayPal")
model = st.subheader("Select LLM Model")
groq_client = GroqClient()
available_models = groq_client.get_available_models()
selected_model = st.selectbox("Choose a model", list(available_models.keys()), index=0)


search_engine = st.selectbox(
    "Select Search Engine",
    options=["Google", "Yandex", "DuckDuckGo", "Bing", "Virus Total", "Shodan", "Hunter How", "Fofa"],
    index=0,
    disabled=True  # Currently only Google is implemented
)

# Step 1: Generate Queries
if st.button("Generate Queries"):
    if brand_name:
        with st.spinner("Generating queries..."):
            #groq_client = GroqClient()
            st.session_state["queries"] = groq_client.generate_dorking_queries(brand_name, selected_model)
        if st.session_state["queries"]:
            st.success(f"Generated {len(st.session_state['queries'])} queries.")
        else:
            st.error("No queries generated. Please try again.")
    else:
        st.error("Brand name cannot be empty.")

# Add a download button for the generated queries
if st.session_state["queries"]:
    st.download_button(
        label="Download Generated Queries",
        data="\n".join(st.session_state["queries"]),
        file_name=f"{brand_name}_generated_queries.txt",
        mime="text/plain"
    )

# Step 2: Execute Searches
if st.button("Execute Searches"):
    if st.session_state["queries"]:
        with st.spinner("Executing searches..."):
            serper_client = SerperClient()
            raw_results = serper_client.execute_queries(st.session_state["queries"])
        if raw_results:
            with st.spinner("Processing search results..."):
                st.session_state["processed_results"] = serper_client.process_search_results(raw_results)
            st.success("Search results processed successfully.")
        else:
            st.error("No results found. Please try again.")
    else:
        st.error("Generate queries first.")

# Download Pre-LLM Analysis Results
if st.session_state["processed_results"]:
    st.download_button(
        label="Download Pre-LLM Analysis Results",
        data="\n".join(map(str, st.session_state["processed_results"])),
        file_name=f"{brand_name}_pre_llm_results.txt",
        mime="text/plain"
    )

# Step 3: Relevancy Analysis
if st.button("LLM Relevancy Analysis"):
    if st.session_state["processed_results"]:
        with st.spinner("Performing relevancy analysis..."):
            relevancy_agent = RelevancyAgent(brand_name)
            st.session_state["relevant_results"] = relevancy_agent.filter_results(st.session_state["processed_results"])
        if st.session_state["relevant_results"]:
            st.success(f"Found {len(st.session_state['relevant_results'])} relevant results.")
        else:
            st.error("No relevant results found.")
    else:
        st.error("Execute searches first.")

# Download Post-LLM Analysis Results
if st.session_state["relevant_results"]:
    st.download_button(
        label="Download Post-LLM Analysis Results",
        data="\n".join(map(str, st.session_state["relevant_results"])),
        file_name=f"{brand_name}_post_llm_results.txt",
        mime="text/plain"
    )

# Clear Session State
if st.button("Clear Data"):
    st.session_state["queries"] = []
    st.session_state["processed_results"] = []
    st.session_state["relevant_results"] = []
    st.success("Session data cleared.")

# Progress Display (Simulated for UI)
if st.session_state["queries"]:
    st.progress(33)
if st.session_state["processed_results"]:
    st.progress(66)
if st.session_state["relevant_results"]:
    st.progress(100)

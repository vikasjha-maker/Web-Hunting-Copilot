import streamlit as st
from modules.groq_client import GroqClient
from modules.serper_client import SerperClient
from modules.relevancyAgent import RelevancyAgent
import os

def main():
    st.set_page_config(page_title="Brand Analysis Tool", layout="wide")
    st.title("🔍 Brand Analysis Tool")
    st.write("Analyze brand data using LLM models and relevancy analysis.")
    
    # Sidebar for user input
    with st.sidebar:
        st.header("Input Parameters")
        brand_name = st.text_input("Enter Brand Name", "").strip()
        if not brand_name:
            st.warning("Please enter a brand name to proceed.")
        
        st.subheader("Select LLM Model")
        groq_client = GroqClient()
        available_models = groq_client.get_available_models()
        selected_model = st.selectbox("Choose a model", list(available_models.keys()), index=0)
        
        st.subheader("Choose Search Engine")
        search_engine = st.radio("Search Engine", ["Google", "Bing"], index=0)
    
    # Initialize session states
    if "processed_results" not in st.session_state:
        st.session_state["processed_results"] = None
    if "relevant_results" not in st.session_state:
        st.session_state["relevant_results"] = None
    
    # Step 1: Generate Queries
    if st.button("Generate Queries"):
        with st.spinner("Generating Google Dork queries..."):
            queries = groq_client.generate_dorking_queries(brand_name, selected_model)
        if queries:
            st.success(f"Generated {len(queries)} queries.")
            st.write(queries)
            
            # Add a download button for generated queries
            st.download_button(
                label="Download Generated Queries",
                data="\n".join(queries),
                file_name=f"{brand_name}_generated_queries.txt",
                mime="text/plain"
            )
        else:
            st.error("No valid queries could be generated.")

    # Step 2: Execute Searches
    if st.button("Execute Searches"):
        with st.spinner("Executing searches..."):
            serper_client = SerperClient()
            raw_results = serper_client.execute_queries(queries)
        
        if raw_results:
            st.session_state["processed_results"] = serper_client.process_search_results(raw_results)
            st.success("Search results processed successfully!")
        else:
            st.error("No search results found.")
    
    # Step 3: Processed Results Download
    if st.session_state["processed_results"]:
        st.subheader("Pre-LLM Analysis Results")
        st.write(st.session_state["processed_results"])
        st.download_button(
            label="Download Pre-LLM Analysis Results",
            data="\n".join(str(st.session_state["processed_results"])),
            file_name=f"{brand_name}_pre_llm_results.txt",
            mime="text/plain"
        )
    
    # Step 4: Relevancy Analysis
    if st.button("Relevancy Analysis"):
        if st.session_state["processed_results"]:
            with st.spinner("Performing relevancy analysis..."):
                relevancy_agent = RelevancyAgent(brand_name)
                st.session_state["relevant_results"] = relevancy_agent.filter_results(st.session_state["processed_results"])
            
            if st.session_state["relevant_results"]:
                st.success("Relevancy analysis completed.")
                st.subheader("Relevant Results")
                st.write(st.session_state["relevant_results"])
                
                # Add download button for relevant results
                st.download_button(
                    label="Download Post-LLM Analysis Results",
                    data="\n".join(str(st.session_state["relevant_results"])),
                    file_name=f"{brand_name}_post_llm_results.txt",
                    mime="text/plain"
                )
            else:
                st.error("No relevant results found after LLM analysis.")
        else:
            st.error("No processed results available for relevancy analysis.")
    
    # Clear session data
    if st.button("Clear Data"):
        st.session_state["processed_results"] = None
        st.session_state["relevant_results"] = None
        st.success("Session data cleared.")

if __name__ == "__main__":
    main()

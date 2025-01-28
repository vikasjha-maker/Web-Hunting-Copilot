import streamlit as st
from modules.groq_client import GroqClient
from modules.serper_client import SerperClient
from modules.relevancyAgent import RelevancyAgent
import gc

def main():
    st.title("Web Hunting Copilot")

    # Sidebar for inputs
    with st.sidebar:
        # Brand name input
        brand_name = st.text_input("Enter brand name to analyze", 
                                 placeholder="e.g., Uber, Netflix, PayPal")
        
        # Model selection
        groq_client = GroqClient()
        available_models = groq_client.get_available_models()
        model = st.selectbox(
            "Select Model",
            options=list(available_models.keys()),
            index=list(available_models.keys()).index("llama3-70b-8192") if "llama3-70b-8192" in available_models else 0
        )
        
        # Search engine selection
        search_engine = st.selectbox(
            "Select Search Engine",
            options=["Google", "Yandex", "DuckDuckGo", "Bing", "Virus Total", "Shodan", "Hunter How", "Fofa"],
            index=0,
            disabled=True  # Currently only Google is implemented
        )
        
        # Search button
        search_button = st.button("Start Search")


    if search_button:
        if not brand_name:
            st.error("Error: Brand name cannot be empty")
            return

        try:
            # Progress bar
            progress_bar = st.progress(0)
            
            # Step 1: Generate queries
            st.subheader("Generating Google Dork Queries")
            queries = groq_client.generate_dorking_queries(brand_name, model)
            progress_bar.progress(0.25)
            
            if not queries:
                st.markdown('''''')
                st.error(f"No valid {st.markdown('''':red[queries]''')} generated")
                st.markdown('''Please try again!''')
                return
            
            # Step 2: Execute searches
            st.subheader("Executing Searches")
            serper_client = SerperClient()
            raw_results = serper_client.execute_queries(queries)
            progress_bar.progress(0.50)
            
            # Step 3: Process results
            if raw_results:
                st.subheader("Processing Search Results")
                processed_results = serper_client.process_search_results(raw_results)
                progress_bar.progress(0.75)
                
                if processed_results:
                    # Store processed results in session state
                    st.session_state.processed_results = processed_results
                    
                    # Add download button for pre-LLM analysis results
                    pre_llm_text = "\n\n".join([f"Link: {result['link']}\n" 
                                              for result in st.session_state.processed_results])
                    st.download_button(
                        label="Download Pre-LLM Analysis Results",
                        data=pre_llm_text,
                        file_name="pre_llm_analysis.txt",
                        mime="text/plain"
                    )
                    
                    # Step 4: Relevancy analysis
                    st.subheader("Analyzing Relevancy")
                    relevancy_agent = RelevancyAgent(brand_name)
                    relevant_results = relevancy_agent.filter_results(st.session_state.processed_results)
                    progress_bar.progress(1.0)
                    
                    if relevant_results:
                        # Store relevant results in session state
                        st.session_state.relevant_results = relevant_results
                        
                        # Add download button for post-LLM analysis results
                        post_llm_text = "\n\n".join([f"Link: {result['link']}\n" 
                                                   for result in st.session_state.relevant_results])
                        st.download_button(
                            label="Download Post-LLM Analysis Results",
                            data=post_llm_text,
                            file_name="post_llm_analysis.txt",
                            mime="text/plain"
                        )
                        
                        # Display results
                        st.subheader(f"Relevant Results ({len(st.session_state.relevant_results)} found)")
                        
                        for i, result in enumerate(st.session_state.relevant_results, 1):
                            with st.expander(f"Result {i}: {result['title']}", expanded=True):
                                st.write(f"**Link:** {result['link']}")
                                st.write(f"**Snippet:** {result['snippet']}")
                                st.markdown("---")
                    else:
                        st.warning("No relevant results found after LLM analysis")
                else:
                    st.error("No results to analyze")
            else:
                st.error("No search results found")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
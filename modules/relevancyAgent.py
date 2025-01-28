from typing import Dict, Any, List
from .groq_client import GroqClient

class RelevancyAgent:
    def __init__(self, brand_name: str):
        self.brand_name = brand_name
        self.groq_client = GroqClient()
        self.system_prompt = """You are a brand relevancy analysis agent. Your task is to determine if a search result is relevant to potential phishing or scam attempts targeting the specified brand.

Analyze the given title, URL, and snippet. Respond with ONLY 'Yes' or 'No'.

Consider these factors:
1. Direct brand name mentions
2. Brand-related keywords
3. Suspicious patterns (login pages, payment forms, data collection)
4. Domain legitimacy
5. Content context

Respond ONLY with 'Yes' if the result appears to be a potential security concern, or 'No' if it's likely legitimate or unrelated."""

    def check_relevancy(self, result: Dict[Any, Any]) -> bool:
        """
        Use Groq LLM to check if a single result is relevant
        Returns: True if relevant, False if not
        """
        # Prepare the content for analysis
        content = f"""
Brand: {self.brand_name}

Result to analyze:
Title: {result.get('title', '')}
URL: {result.get('link', '')}
Description: {result.get('snippet', '')}

Is this result relevant to potential phishing/scam attempts targeting {self.brand_name}?
"""
        # Get LLM's analysis
        response = self.groq_client.generate_completion(
            system_prompt=self.system_prompt,
            user_prompt=content,
            temperature=0.1,  # Lower temperature for more consistent yes/no responses
            stream=False  # We want direct responses for this task
        )
        
        # Clean and check the response
        if response:
            response = response.strip().lower()
            return response == 'yes'
        return False

    def filter_results(self, results: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        """
        Filter results using LLM-based relevancy checking
        """
        relevant_results = []
        total_results = len(results)
        
        print(f"\n=== Analyzing {total_results} results for {self.brand_name} relevancy using Groq LLM ===")
        
        for i, result in enumerate(results, 1):
            print(f"\nAnalyzing result {i}/{total_results}")
            print(f"Title: {result.get('title', '')}")
            print(f"Link: {result.get('link', '')}")
            
            is_relevant = self.check_relevancy(result)
            print(f"LLM Analysis - Relevant: {'Yes' if is_relevant else 'No'}")
            
            if is_relevant:
                relevant_results.append(result)
                
            # Add a small delay between requests if needed
            # time.sleep(0.5)
        
        print(f"\n=== LLM Relevancy Analysis Complete ===")
        print(f"Total results analyzed: {total_results}")
        print(f"Relevant results found: {len(relevant_results)}")
        print(f"Results filtered out: {total_results - len(relevant_results)}")
        
        return relevant_results
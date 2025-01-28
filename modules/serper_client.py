from dotenv import load_dotenv
import os
import requests
import time
import json
from datetime import datetime
from typing import Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SerperClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        self.base_url = "https://google.serper.dev/search"
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.session.headers.update({
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })

    def search(self, query: str, max_retries: int = 3) -> Dict[Any, Any]:
        """Execute a search query using Serper API with retries"""
        payload = {
            'q': query,
            'num': 100
        }

        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.Timeout:
                wait_time = (attempt + 1) * 2
                print(f"\nTimeout error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            except requests.exceptions.RequestException as e:
                print(f"\nError executing search: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return {}
        
        print("\nMax retries exceeded. Skipping query.")
        return {}

    def execute_queries(self, queries: List[str]) -> List[Dict[Any, Any]]:
        """Execute multiple search queries and return combined results"""
        all_results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\nProcessing query {i}/{len(queries)}")
            print(f"Query: {query}")
            
            results = self.search(query)
            if results:
                all_results.append(results)
                print(f"Found results for query {i}")
            else:
                print(f"No results found for query {i}")
        
        return all_results

    def process_search_results(self, results: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        """Process and clean search results"""
        processed_results = []
        
        for result_set in results:
            if not isinstance(result_set, dict):
                continue
                
            organic = result_set.get('organic', [])
            if organic:
                for item in organic:
                    processed_result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'position': item.get('position', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    processed_results.append(processed_result)
        
        return processed_results

'''
    def save_results(self, results: List[Dict[Any, Any]], brand_name: str) -> None:
        """Save results to a JSON file in the outputs directory within the project"""
        try:
            # Get the current script's directory
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            outputs_dir = os.path.join(current_dir, "outputs")
            
            # Create outputs directory if it doesn't exist
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{brand_name}_results_{timestamp}.json"
            file_path = os.path.join(outputs_dir, filename)
            
            # Save the results
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nResults saved to: {file_path}")
            # Add these debug lines
            print(f"\nAbsolute path to saved file: {os.path.abspath(file_path)}")
            print(f"Directory contents:")
            print(os.listdir(outputs_dir))
            
        except Exception as e:
            print(f"\nError saving results: {str(e)}")
            # Try saving to current directory as fallback
            try:
                current_dir = os.getcwd()
                outputs_dir = os.path.join(current_dir, "outputs")
                
                if not os.path.exists(outputs_dir):
                    os.makedirs(outputs_dir)
                    
                fallback_path = os.path.join(outputs_dir, f"{brand_name}_results_{timestamp}.json")
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"Results saved to: {fallback_path}")
            except Exception as e2:
                print(f"Failed to save results: {str(e2)}")
'''
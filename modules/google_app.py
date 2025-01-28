from dotenv import load_dotenv
import os
import json
import requests
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import google.generativeai as genai

class GroqClient:
    # Define available models and their capabilities
    MODELS = {
        "gemini-1.5-pro": "Best balance (Recommended)",
        "gemini-1.5-flash": "Large context",
        "gemini-1.5-flash-8b": "Fast",
        "gemini-2.0-flash-exp": "High quality"
    }
    
    ModelType = Literal[
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-2.0-flash-exp"
    ]

    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)
        
        # Define the system prompt
        self.system_prompt = """You are an expert in Google Dorking. Generate advanced Google search queries to detect potential phishing, scam, and malicious content for targeting {brand_name}. Return results in a JSON array format.

Each query must combine:
1. Hosting platforms (2-3 per query)
2. Brand keywords and variations
3. Relevant operators (intext, intitle, inurl)
4. Exclusion of legitimate domains

Focus areas:
1. Login and authentication pages
2. Payment and financial forms
3. Personal data collection
4. Promotional scams
5. Malicious file downloads
6. Brand impersonation

Each object must have:
- "category": Add the categories
- "query": The Google dork query string
- "purpose": Brief description of what the query aims to find

Return ONLY the JSON array of queries without any additional explanation."""

    def get_available_models(self):
        """Returns a dictionary of available models and their capabilities"""
        return self.MODELS

    def generate_brand_specific_prompt(self, brand_name: str) -> str:
        """Generate a brand-specific user prompt"""
        hosting_platforms = [
            ".cprapid.com", ".topfi.io", ".sites.google.com", ".gitbook.io",
            "vercel.app", "netlify.app", ".jimdofree.com", ".glitch.me",
            ".000webhostapp.com", ".godaddysites.com", ".weebly.com",
            ".linea.build", ".consensys.net", ".waterbridgemedia.ca",
            ".acodemy.io", ".appspot.com", ".hedron.pro", ".ic0.app",
            ".scroll.io", ".webador.com", ".mypixieset.com", ".mystrikingly.com",
            ".webador.com", ".amazonaws.com", ".aippnet.org", ".powerloom.io",
            ".bemular.net", ".sitey.me", ".inmotionhosting.com", ".flazio.com",
            ".teachable.com", ".herokuapp.com", ".site123.me", ".yolasite.com",
            ".sibforms.com", ".boxmode.io", ".webydo.com", ".xindaim.net",
            ".jotform.com", ".fillout.com", ".zoho.com", ".getresponsesite.com"
        ]
        
        return f"""Generate Google dork queries to find potential phishing and scam content targeting {brand_name}.
Focus areas for {brand_name}:

Step 1:You are tasked with identifying phishing and scam websites related to a specific brand. Your first task is to gather relevant information about the brand. This includes the brand name, its logo, common keywords, popular products, official URLs, etc. Ensure you collect:
    - Brand name
    - Website URLs (official domain names)
    - Commonly associated keywords (e.g., "free offer", "gift card", "login", "discount")
    - Popular product names or services
    - The brand's logo and any frequently used imagery or slogans
Ensure that you compile a list of terms, services, and content that could be used by scammers to impersonate the brand.
    
Step 2: Using the brand information you collected in Step 1, generate advanced Google Dorking queries to find potentially phishing or scam pages. Focus on the following techniques:
Use these Google dork Brand-based search and Advanced Search Operators effectively:
- intext, allintext: for content detection
- intitle, allintitle: for page titles
- inurl, allinurl: for URL analysis
- site: for domain targeting
- filetype: for specific file types
- OR, AND operators for combining terms
- Minus (-) operator for excluding domains
- Use of the following additional operators:
  - allintext: Searches for occurrences of all keywords given
  - inurl: Searches for a URL matching one of the keywords
  - intitle: Searches for occurrences of keywords in title
  - allinurl: Searches for a URL matching all the keywords
  - numrange: Used to locate specific numbers in your searches
  - before/after: Used to search within a particular date range
  - related: Lists web pages that are 'similar' to a specified web page
  - cache: Shows the version of the web page that Google has in its cache

List of Phish/Scam related Keywords and Use this list to generate more targeted queries:
    Keywords: payment, credit card, billing, support, tech support, secure, verified, trusted, official, certificate, discount, 
    offer, promo, deal, official, verify, support, help, reset, password, verify, account, Free, offer, coupon, 
    gift card, credit, reward, bonus, Clone, verify, login, sign-in, Password reset forms, win, enter credentials, 
    Account verification pages, "too good to be true", “fake job offers” or “get rich quick”, "index of /"
    alongside the brand name.
    
Step 3: Typo-Squatting URL Generation:
Use a permutation and combination technique to generate URLs that could potentially trick users by mimicking the {brand_name} official website. Generate misspelled versions of the brand's domain name, including variations like:
    Common typos (e.g., "amazn.com" instead of "amazon.com")
    Adding extra words (e.g., "brand-name-discount.com")
    Swapping characters (e.g., "brnad.com" for "brand.com")
    Prefixes or suffixes added to domain (e.g., "brandname-free.com")

Step 4: Analyzing the Results

    1. Google Dorking Results:
        Review the results from Google Dorking for potential phishing or scam websites. Filter for websites that:
            Ask for personal information like usernames, passwords, or credit card details.
            Promote suspicious offers like “too good to be true” discounts or free giveaways.
            Use deceptive tactics to impersonate the brand, like using a nearly identical domain name or copying content from the {brand_name} official website.   
    2.  Typo-Squatted Results:
        Check the typo-squatted URLs to see if they are impersonating the brand. Focus on domains that:
        Have very similar names but are slightly altered.
        Use deceptive TLDs (top-level domains) or country-code TLDs to appear legitimate.
        Contain phishing-like content or prompts that encourage the user to input sensitive information.

Step 5: Verification of Scam/Phishing Content:    

    1. Phishing Indicators:
        Check if the site asks users to enter credentials, financial information, or personal data.
        Look for red flags like:
            Poor grammar and spelling.
            Too good to be true offers.
            Requests for email or login credentials with no clear reason.
            Lack of SSL certificates (no “https://”).
        Ensure that the branding or logo used on the site matches the official brand identity (including image quality, color schemes, fonts, and logo positioning).

    2. Scam Offers:
        If the site claims discounts or giveaways, verify if the offer is too enticing (e.g., “win an iPhone for $1”).
        Look for content related to fake contests, prizes, or "limited time" offers that are typically associated with scams.  

    
    3. Second Agent Verification:

    Once you have bifurcated the results, pass them to the second agent, who will focus on the authenticity of the site and verify if it's a genuine scam or phishing attempt.         


Required Query Structure:
Use these hosting platforms: {', '.join(hosting_platforms)}

Create queries that detect:
1. Authentication pages:
   - Login forms
   - Password reset
   - Account verification

2. Financial scams:
   - Payment forms
   - Credit card collection
   - Gift card offers

3. Data collection:
   - Personal information forms
   - Support impersonation
   - Credential theft

4. Brand abuse:
   - Logo misuse
   - Company impersonation
   - Fake promotions

5. Malicious content:
   - File downloads (.exe, .zip, .pdf)
   - Phishing kits
   - Malware distribution


Special focus on:
1. Form detection: (allintext:"password" OR allintext:"login" OR allintext:"sign in")
2. Promotional content: (intitle:"discount" OR intitle:"offer" OR allintext:"coupon")
3. Brand assets: (inurl:"logo" OR intitle:"brand" OR inanchor:"official")
4. Trust markers: (allintext:"secure payment" OR intext:"verified" OR intext:"trusted")

Each query must:
- Use 2-3 or as many hosting platforms
- Include {brand_name} and related keywords
- Utilize appropriate Google dork operators
- Exclude {brand_name}.com

Each object must have:
- "category": Add the categories
- "query": The Google dork query string
- "purpose": Brief description of what the query aims to find

Example Usgae:
site:.vercel.app OR site:.netlify.app) intext:{brand_name}  -site:{brand_name}.com
Generate at least 20 queries targeting these areas."""

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: ModelType = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 1,
        stream: bool = True,
        stop: Optional[list] = None
    ):
        """
        Generate completion using Google's Generative AI
        """
        if model not in self.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(self.MODELS.keys())}")

        try:
            # Add safety configuration            
            safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        }

            # Configure the model
            model_instance = genai.GenerativeModel(model_name=model,safety_settings=safety_settings)
            
            # Combine system and user prompts
            combined_prompt = f"{system_prompt}\n\nUser: {user_prompt}"
            
            # Generate response
            if stream:
                response = model_instance.generate_content(
                    combined_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        top_p=top_p,
                        max_output_tokens=max_tokens,
                    ),
                    stream=True
                )
                
                # Handle streaming response
                full_response = ""
                for chunk in response:
                    chunk_text = chunk.text
                    full_response += chunk_text
                    print(chunk_text, end="", flush=True)
                return full_response
            else:
                response = model_instance.generate_content(
                    combined_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        top_p=top_p,
                        max_output_tokens=max_tokens,
                    )
                )
                return response.text

        except Exception as e:
            print(f"\nError during query generation: {str(e)}")
            if stream:
                print("\nRetrying with non-streaming mode...")
                return self.generate_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False
                )
            return None

    def parse_queries(self, response: str) -> List[str]:
        """Extract queries from the response with improved parsing"""
        try:
            # Clean the response
            cleaned_response = response.strip()
            if "```" in cleaned_response:
                blocks = cleaned_response.split("```")
                for block in blocks:
                    if '[' in block and ']' in block:
                        cleaned_response = block.strip()
                        break
                if cleaned_response.lower().startswith('json'):
                    cleaned_response = cleaned_response[4:].strip()

            # Parse JSON
            data = json.loads(cleaned_response)
            
            # Initialize list for valid queries
            valid_queries = []
            
            # Handle both array of objects and array of strings
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'query' in item:
                        # Extract query from object format
                        query = item['query'].strip().strip('"').strip("'")
                        if 'site:' in query:
                            valid_queries.append(query)
                    elif isinstance(item, str) and 'site:' in item:
                        # Handle direct string format
                        query = item.strip().strip('"').strip("'")
                        valid_queries.append(query)
            
            if valid_queries:
                print(f"\nSuccessfully extracted {len(valid_queries)} queries")
                return valid_queries
            else:
                print("\nNo valid queries found in the response")
                print("Raw response format:", type(data))
                return []

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Raw response:", response)
            return []

    def generate_dorking_queries(self, brand_name: str, model: ModelType = "gemini-1.5-pro") -> List[str]:
        """Generate dorking queries for a specific brand"""
        user_prompt = self.generate_brand_specific_prompt(brand_name)
        response = self.generate_completion(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            model=model
        )        
        if response:
            queries = self.parse_queries(response)
            print(f"\nGenerated {len(queries)} queries successfully")
            return queries
        return []

    def validate_query(self, query: str) -> bool:
        """Validate if a query is properly formatted"""
        required_operators = ['site:', 'intext:', 'intitle:']
        return any(op in query for op in required_operators) and '-site:' in query



class SerperClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        self.base_url = "https://google.serper.dev/search"
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
        )
        
        # Create session with retry strategy
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
                    timeout=30  # 30 seconds timeout
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


def process_search_results(results: Dict[Any, Any]) -> List[Dict[str, Any]]:
    """Process and format search results"""
    processed_results = []
    
    if 'organic' not in results:
        return processed_results

    for result in results['organic']:
        processed_results.append({
            'title': result.get('title', ''),
            'link': result.get('link', ''),
            'snippet': result.get('snippet', ''),
            'position': result.get('position', 0)
        })
    
    return processed_results


def save_results(results: List[Dict[str, Any]], filename: str):
    """Save results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_results': len(results),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {filename}")

def main():
    try:
        # Initialize clients
        groq = GroqClient()
        serper = SerperClient()

        # Print available models
        print("\n=== Available Models ===")
        for model, capability in groq.get_available_models().items():
            print(f"- {model}: {capability}")
        
        # Get brand name from user
        print("\n=== Brand Analysis ===")
        brand_name = input("Enter brand name to analyze(e.g., Uber, Netflix, PayPal)): ").strip().lower()
        if not brand_name:
            raise ValueError("Brand name cannot be empty")
        
        model = input(f"Enter model name (default: gemini-1.5-pro): ").strip() or "gemini-1.5-pro"
        if model not in groq.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(groq.MODELS.keys())}")
        
        # Generate queries
        print("\n=== Generating Queries ===")
        queries = groq.generate_dorking_queries(brand_name)
        if not queries:
            raise ValueError("No valid queries generated")
        
        # Process each query
        print("\n=== Executing Searches ===")
        all_results = []
        
        for i, query in enumerate(queries, 1):
            if groq.validate_query(query):
                print(f"\nProcessing query {i}/{len(queries)}")
                print(f"Query: {query}")
                
                results = serper.search(query)
                processed_results = process_search_results(results)
                
                if processed_results:
                    all_results.extend(processed_results)
                    print(f"Found {len(processed_results)} results")
                else:
                    print("No results found")
        
        # Save results
        if all_results:
            save_results(all_results, f"{brand_name}_search_results")
            print(f"\n=== Analysis Complete ===")
            print(f"Total results found: {len(all_results)}")
        else:
            print("\nNo results found for any query")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
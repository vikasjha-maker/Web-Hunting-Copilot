from modules.groq_client import GroqClient
from modules.serper_client import SerperClient
from modules.relevancyAgent import RelevancyAgent
import os
def main():
    print("\n=== Brand Analysis Tool ===")
    
    # Get brand name
    brand_name = input("\nEnter brand name to analyze: ").strip()
    if not brand_name:
        print("Error: Brand name cannot be empty")
        return 1
    
    try:
        # Step 1: Generate queries using Groq
        groq_client = GroqClient()
        print("\n=== Available Models ===")
        for model, capability in groq_client.get_available_models().items():
            print(f"- {model}: {capability}")
        
        model = input(f"\nEnter model name (default: llama3-70b-8192): ").strip() or "llama3-70b-8192"
        print("\n=== Generating Google Dork Queries ===")
        queries = groq_client.generate_dorking_queries(brand_name, model)
        
        if not queries:
            print("No valid queries generated")
            return 1
        
        print(f"\nGenerated {len(queries)} search queries")
        
        # Step 2: Execute searches using Serper
        print("\n=== Executing Searches ===")
        serper_client = SerperClient()
        raw_results = serper_client.execute_queries(queries)
        
        # Step 3: Process initial results
        if raw_results:
            print("\n=== Processing Search Results ===")
            processed_results = serper_client.process_search_results(raw_results)
            
            if processed_results:
                # Step 4: LLM-based relevancy analysis
                print("\n=== Starting Agent Relevancy Analysis ===")
                relevancy_agent = RelevancyAgent(brand_name)
                relevant_results = relevancy_agent.filter_results(processed_results)
                
                if relevant_results:
                    # Display sample of relevant results
                    print("\n=== Sample of Relevant Results ===")
                    sample_size = min(5, len(relevant_results))
                    for i, result in enumerate(relevant_results[:sample_size], 1):
                        print(f"\nRelevant Result {i}/{sample_size}:")
                        print(f"Title: {result['title']}")
                        print(f"Link: {result['link']}")
                        print(f"Snippet: {result['snippet'][:200]}...")
                    
                    print(f"\nTotal relevant results found: {len(relevant_results)}")
                    
                    # Save results to output file
                    output_dir = "output"
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{brand_name}_results.txt")
                    
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(f"=== Brand Analysis Results for {brand_name} ===\n")
                        f.write(f"Total relevant results found: {len(relevant_results)}\n\n")
                        for i, result in enumerate(relevant_results, 1):
                            f.write(f"Result {i}/{len(relevant_results)}:\n")
                            f.write(f"Title: {result['title']}\n")
                            f.write(f"Link: {result['link']}\n")
                            f.write(f"Snippet: {result['snippet']}\n")
                            f.write("\n" + "="*50 + "\n\n")
                    
                    print(f"\nResults have been saved to: {output_file}")
                    return 0
                    
                    return 0
                else:
                    print("\nNo relevant results found after LLM analysis")
                    return 1
            else:
                print("\nNo results to analyze")
                return 1
        else:
            print("\nNo search results found")
            return 1
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
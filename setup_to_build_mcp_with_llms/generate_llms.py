import logging
import time
from firecrawl import FirecrawlApp

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the client
firecrawl = FirecrawlApp(api_key="fc-37a7af4e01d245648cd514b401c18cce")

# Define generation parameters
params = {
    "maxUrls": 900,  # Maximum URLs to analyze
    "showFullText": True  # Include full text in results
}

# Function to create llms.txt and llms-full.txt files
def create_llm_files(llmstxt, llmsfulltxt):
    logging.info("Creating cohere-llms.txt and cohere-llms-full.txt files.")
    
    # Create llms.txt
    with open('cohere-llms.txt', 'w') as llms_file:
        llms_file.write(llmstxt)
    logging.info("cohere-llms.txt created successfully.")

    # Create llms-full.txt if full text is available
    if llmsfulltxt:
        with open('cohere-llms-full.txt', 'w') as llms_full_file:
            llms_full_file.write(llmsfulltxt)
        logging.info("cohere-llms-full.txt created successfully.")
    else:
        logging.warning("No full text available; cohere-llms-full.txt not created.")

# Create async job
job = firecrawl.async_generate_llms_text(
    url="https://cohere.com",
    params=params
)

if job['success']:
    job_id = job['id']

    # Continuously check LLMs.txt generation status
    while True:
        status = firecrawl.check_generate_llms_text_status(job_id)

        # Log current status
        logging.info(f"Status: {status['status']}")

        if status['status'] == 'completed':
            logging.info("LLMs.txt Content: %s", status['data']['llmstxt'])
            if 'llmsfulltxt' in status['data']:
                logging.info("Full Text Content: %s", status['data']['llmsfulltxt'])
            
            # Call the function to create the files
            create_llm_files(status['data']['llmstxt'], status['data'].get('llmsfulltxt', ''))
            processed_urls_count = status['data'].get('processedUrls', None)
            if processed_urls_count is not None:
                logging.info("Processed URLs: %d", len(processed_urls_count))
            else:
                logging.info("Processed URLs key not found; continuing without it.")
            break
        elif status['status'] == 'failed':
            logging.error("Job failed.")
            break
        else:
            logging.info("Job is still in progress. Checking again in 30 seconds.")
            time.sleep(30)
else:
    logging.error("Error: %s", job.get('error', 'Unknown error'))
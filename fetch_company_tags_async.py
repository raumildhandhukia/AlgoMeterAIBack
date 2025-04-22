#!/usr/bin/env python3
"""
Async script to fetch company tags for all LeetCode questions from a CSV file.
Sends requests to the company-tags endpoint and tracks failed requests.
"""

import asyncio
import aiohttp
import csv
import time
from datetime import datetime
import urllib.parse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://big-o-insights-back.vercel.app"
CSV_PATH = "data/leetcode_questions_complete.csv"
ERROR_CSV_PATH = f"failed_company_tags_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
CONCURRENCY_LIMIT = 5000  # Reduced to avoid rate limiting
TIMEOUT = 60  # Request timeout in seconds
RETRY_COUNT = 2  # Number of retries for failed requests

async def fetch_company_tags(session, url, question_id, question_name, retries=RETRY_COUNT):
    """Fetch company tags for a given LeetCode problem URL."""
    encoded_url = urllib.parse.quote(url)
    api_url = f"{BASE_URL}/company-tags?url={encoded_url}"
    
    for attempt in range(retries + 1):
        try:
            async with session.get(api_url, timeout=TIMEOUT) as response:
                status = response.status
                
                if status == 200:
                    logger.info(f"Success: {question_id} - {question_name}")
                    return True, None
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed ({status}): {question_id} - {question_name}")
                    
                    if attempt < retries:
                        logger.info(f"Retrying {question_id} - {question_name} (Attempt {attempt+1}/{retries})")
                        await asyncio.sleep(2)  # Longer delay before retry
                    else:
                        return False, f"HTTP {status}: {error_text[:100]}"
        except asyncio.TimeoutError:
            logger.warning(f"Timeout: {question_id} - {question_name}")
            if attempt < retries:
                logger.info(f"Retrying {question_id} - {question_name} (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(1)
            else:
                return False, "Request timeout"
        except Exception as e:
            logger.warning(f"Error: {question_id} - {question_name} - {str(e)}")
            if attempt < retries:
                logger.info(f"Retrying {question_id} - {question_name} (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(1)
            else:
                return False, str(e)
    
    return False, "Max retries exceeded"

async def process_batch(session, batch):
    """Process a batch of questions concurrently with rate limiting."""
    # Add semaphore to limit concurrent requests even within a batch
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    """Process a batch of questions concurrently."""
    async def fetch_with_semaphore(question):
        async with semaphore:
            # Small random delay to spread out requests
            await asyncio.sleep(0.1 + (0.2 * asyncio.get_event_loop().time() % 1.0))
            return await fetch_company_tags(
                session, 
                question['url'], 
                question['id'], 
                question['name']
            )
    
    tasks = [fetch_with_semaphore(question) for question in batch]
    
    results = await asyncio.gather(*tasks)
    
    failed_questions = []
    for i, (success, error) in enumerate(results):
        if not success:
            failed_questions.append({
                'id': batch[i]['id'],
                'name': batch[i]['name'],
                'url': batch[i]['url'],
                'error': error
            })
    
    return failed_questions

async def main():
    """Main function to process all questions."""
    start_time = time.time()
    logger.info(f"Starting company tags fetch process at {datetime.now()}")
    
    # Read questions from CSV
    questions = []
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append({
                    'id': row['id'],
                    'name': row['name'],
                    'url': row['url']
                })
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return
    
    logger.info(f"Loaded {len(questions)} questions from CSV")
    
    # Process questions in batches
    failed_questions = []
    
    async with aiohttp.ClientSession() as session:
        # Create batches based on concurrency limit
        batches = [questions[i:i + CONCURRENCY_LIMIT] for i in range(0, len(questions), CONCURRENCY_LIMIT)]
        logger.info(f"Processing {len(batches)} batches with up to {CONCURRENCY_LIMIT} concurrent requests per batch")
        
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)} with {len(batch)} questions")
            batch_failed = await process_batch(session, batch)
            failed_questions.extend(batch_failed)
            
            # Longer delay between batches to avoid overwhelming the server
            if i < len(batches) - 1:
                await asyncio.sleep(3)
    
    # Write failed questions to CSV
    if failed_questions:
        logger.info(f"Writing {len(failed_questions)} failed questions to {ERROR_CSV_PATH}")
        with open(ERROR_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'url', 'error'])
            writer.writeheader()
            writer.writerows(failed_questions)
    else:
        logger.info("All requests completed successfully!")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Process completed in {elapsed_time:.2f} seconds")
    logger.info(f"Total questions: {len(questions)}")
    logger.info(f"Failed questions: {len(failed_questions)}")
    logger.info(f"Success rate: {(len(questions) - len(failed_questions)) / len(questions) * 100:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())

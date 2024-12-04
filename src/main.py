import logging
import os
from datetime import datetime
from fortune500_scraper import Fortune500Scraper
from dns_scanner import DNSScanner
from checkpoint_manager import CheckpointManager
import json

def setup_logging():
    """Sets up logging configuration."""
    log_dir = "../logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"scan_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        scraper = Fortune500Scraper()
        scanner = DNSScanner()
        checkpoint_mgr = CheckpointManager()
        
        # Load checkpoint if exists
        checkpoint = checkpoint_mgr.load_latest_checkpoint()
        if checkpoint:
            processed_domains = set(checkpoint["processed_domains"])
            results = checkpoint["results"]
            logger.info(f"Resuming from checkpoint with {len(processed_domains)} processed domains")
        else:
            processed_domains = set()
            results = {}
        
        # Get Fortune 500 companies
        companies = scraper.get_companies()
        
        # Process each company
        for company in companies:
            if company in processed_domains:
                logger.info(f"Skipping already processed domain: {company}")
                continue
                
            try:
                # Scan DNS records
                dns_records = scanner.scan_domain(company)
                
                # Check for OpenAI string
                has_openai = scanner.check_openai_string(dns_records)
                
                # Store results
                results[company] = {
                    "dns_records": dns_records,
                    "has_openai": has_openai
                }
                
                processed_domains.add(company)
                
                # Save checkpoint every 10 companies
                if len(processed_domains) % 10 == 0:
                    checkpoint_mgr.save_checkpoint(list(processed_domains), results)
                    
            except Exception as e:
                logger.error(f"Error processing {company}: {str(e)}")
                # Save checkpoint on error
                checkpoint_mgr.save_checkpoint(list(processed_domains), results)
                continue
        
        # Save final results
        checkpoint_mgr.save_checkpoint(list(processed_domains), results)
        
        # Print summary
        openai_count = sum(1 for r in results.values() if r["has_openai"])
        logger.info(f"Scan completed. Found {openai_count} companies with 'openai' in DNS records")

        # write the has_openai=True results to a file
        with open("data/has_openai.json", "w") as f:
            for domain, data in results.items():
                if data["has_openai"]:
                    f.write(f"{domain}\n")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
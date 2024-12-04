import dns.resolver
import logging
from typing import List, Dict
import time
import json
import os

class DNSScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5.0
        self.resolver.lifetime = 5.0
        self.record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS']
        self.successful_records = {}

    def scan_domain(self, domain: str) -> Dict:
        """Scans a domain for all DNS records."""
        results = {}
        has_records = False
        self.logger.info(f"\n\n=== Scanning DNS records for {domain} ===")
        
        for record_type in self.record_types:
            try:
                answers = self.resolver.resolve(domain, record_type)
                records = [str(answer) for answer in answers]
                if records:  # Only add if we got records
                    results[record_type] = records
                    has_records = True
                    # Print results in a readable format
                    print(f"\n{record_type} records for {domain}:")
                    for record in records:
                        print(f"  → {record}")
                time.sleep(0.1)
            except dns.resolver.NXDOMAIN:
                print(f"\n{record_type} records for {domain}: Domain does not exist")
            except dns.resolver.NoAnswer:
                print(f"\n{record_type} records for {domain}: No record exists")
            except dns.resolver.Timeout:
                print(f"\n{record_type} records for {domain}: Query timed out")
            except dns.resolver.NoNameservers:
                print(f"\n{record_type} records for {domain}: No nameservers available")
            except Exception as e:
                print(f"\n{record_type} records for {domain}: Error - {str(e)}")
        
        # Only add to successful records if we found any records
        if has_records:
            self.successful_records[domain] = results
            
            # Print a summary of successful records
            print("\n=== Summary of DNS records ===")
            print(json.dumps(results, indent=2))
            print("=" * 50 + "\n")
            
            # Save to file after each successful scan
            self.save_results()
                
        return results

    def check_openai_string(self, dns_records: Dict) -> bool:
        """Checks if 'openai' string exists in any DNS record."""
        found = False
        for record_type, records in dns_records.items():
            for record in records:
                if 'openai' in record.lower():
                    print(f"\nFound 'openai' in {record_type} record: {record}")
                    found = True
        return found

    def save_results(self):
        """Saves successful DNS records to a JSON file."""
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save the results
        with open("data/results.json", "w") as f:
            json.dump(self.successful_records, f, indent=2)
            self.logger.info(f"Saved {len(self.successful_records)} records to data/results.json")
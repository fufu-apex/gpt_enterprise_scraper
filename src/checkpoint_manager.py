import json
import os
import logging
from typing import List, Dict
from datetime import datetime

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = "../data/checkpoints"):
        self.logger = logging.getLogger(__name__)
        self.checkpoint_dir = checkpoint_dir
        self.ensure_checkpoint_dir()
        
    def ensure_checkpoint_dir(self):
        """Creates checkpoint directory if it doesn't exist."""
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)
            self.logger.info(f"Created checkpoint directory at {self.checkpoint_dir}")

    def save_checkpoint(self, processed_domains: List[str], results: Dict):
        """Saves current progress to a checkpoint file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{timestamp}.json")
        
        checkpoint_data = {
            "processed_domains": processed_domains,
            "results": results,
            "timestamp": timestamp
        }
        
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f)
            self.logger.info(f"Checkpoint saved: {checkpoint_file}")
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {str(e)}")

    def load_latest_checkpoint(self) -> Dict:
        """Loads the most recent checkpoint."""
        try:
            checkpoint_files = [f for f in os.listdir(self.checkpoint_dir) if f.startswith("checkpoint_")]
            if not checkpoint_files:
                return None
                
            latest_checkpoint = max(checkpoint_files)
            checkpoint_path = os.path.join(self.checkpoint_dir, latest_checkpoint)
            
            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            self.logger.info(f"Loaded checkpoint: {checkpoint_path}")
            return checkpoint_data
            
        except Exception as e:
            self.logger.error(f"Error loading checkpoint: {str(e)}")
            return None 
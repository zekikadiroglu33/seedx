import time
import random
from threading import Lock
from typing import Any, List


from classification.schema import ClassificationResult
from utils.seed_id_provider import generate_seed_id  
import torch
# For mock GPU processing
# torch.cuda.is_available()


class ClassificationService:
    def __init__(self):
        self.batch: List[bytes] = []
        self.batch_lock = Lock()
        self.max_batch_size = 32
        self.max_latency_ms = 100
        self.sampling_rate = 0.05  # 5% sampling
        self.batch_start_time = time.time()
        
        # Mock GPU model
        self.model = torch.nn.Sequential(
            torch.nn.Linear(1, 1)
            )
        
    def process_image(self, image_data: bytes) -> Any:
        """Process a single image with batching"""
        with self.batch_lock:
            self.batch.append(image_data)
            
            # Check if we should process the batch
            if (len(self.batch) >= self.max_batch_size or 
                (time.time() - self.batch_start_time) * 1000 >= self.max_latency_ms):
                results = self._process_batch()
                self.batch.clear()
                self.batch_start_time = time.time()
                return results 
            
        # If we didn't process, return a pending response
        return ClassificationResult(
            seed_id=generate_seed_id(),
            classification="pending",
            is_sampled=False,
            image_path="."
        )
    
    def _process_batch(self) -> Any:
        """Process the current batch on the mock GPU"""
        # Simulate GPU processing delay (1-5ms per image)
        processing_time = random.uniform(0.001, 0.005) * len(self.batch)
        time.sleep(processing_time)
        
        results = []
        for image in self.batch:
            # Mock classification (80% accept rate)
            classification = "accept" if random.random() < 0.8 else "reject"
            is_sampled = random.random() < self.sampling_rate
            
            result = ClassificationResult(
                seed_id=generate_seed_id(),
                classification=classification,
                is_sampled=is_sampled,
                image_path="."  # In a real scenario, this would be the path to the saved image
            )
            
            if is_sampled:
                result.image_path = None
                
            results.append(result)
        
        return results
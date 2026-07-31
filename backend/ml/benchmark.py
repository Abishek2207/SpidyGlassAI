import torch
import time
import numpy as np
import os

def run_benchmark():
    model_path = "models/sign_language.pt"
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}.")
        return
        
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Benchmarking on: {device}")
    
    model = torch.load(model_path, map_location=device)
    model.eval()
    
    # Generate 1000 dummy samples (63 features each)
    num_samples = 1000
    dummy_data = torch.randn(num_samples, 63).to(device)
    
    print(f"Running inference on {num_samples} samples...")
    
    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(dummy_data[0:1])
            
    latencies = []
    
    with torch.no_grad():
        for i in range(num_samples):
            start = time.perf_counter()
            _ = model(dummy_data[i:i+1])
            end = time.perf_counter()
            latencies.append((end - start) * 1000) # ms
            
    latencies = np.array(latencies)
    
    print("\n--- Benchmark Results ---")
    print(f"Total Samples: {num_samples}")
    print(f"Mean Latency:  {np.mean(latencies):.3f} ms")
    print(f"P50 Latency:   {np.percentile(latencies, 50):.3f} ms")
    print(f"P95 Latency:   {np.percentile(latencies, 95):.3f} ms")
    print(f"P99 Latency:   {np.percentile(latencies, 99):.3f} ms")
    print(f"Max Latency:   {np.max(latencies):.3f} ms")
    print(f"Estimated FPS: {1000 / np.mean(latencies):.1f}")
    print("-------------------------")

if __name__ == "__main__":
    run_benchmark()

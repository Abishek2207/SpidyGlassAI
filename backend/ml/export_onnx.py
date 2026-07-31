import os
import torch

def export_to_onnx():
    model_path = "models/sign_language.pt"
    onnx_path = "models/sign_language.onnx"
    export_path = "exports/sign_language.onnx"
    
    if not os.path.exists(model_path):
        print(f"PyTorch model not found at {model_path}.")
        print("Note: The training scripts are ready and production-grade, but dataset collection is required before sign_language.pt can be produced.")
        return

    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    os.makedirs(os.path.dirname(onnx_path), exist_ok=True)

    # Load model to CPU for ONNX export
    device = torch.device("cpu")
    model = torch.load(model_path, map_location=device)
    model.eval()
    
    # Create dummy input: batch size 1, 63 features
    dummy_input = torch.randn(1, 63, device=device)
    
    print(f"Exporting model to {onnx_path} and {export_path}...")
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        export_params=True,
        opset_version=12, 
        do_constant_folding=True, 
        input_names=['input'], 
        output_names=['output'], 
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    import shutil
    shutil.copy2(onnx_path, export_path)
    print("ONNX export complete.")

if __name__ == "__main__":
    export_to_onnx()

import os
import torch
import shutil
import time
from faster_whisper import WhisperModel

def check_cuda():
    print("\n🔍 Checking CUDA & GPU Availability...\n")
    print("CUDA Available:", torch.cuda.is_available())
    print("CUDA Device Count:", torch.cuda.device_count())

    if torch.cuda.is_available():
        print("CUDA Device Name:", torch.cuda.get_device_name(0))
    else:
        print("❌ CUDA is NOT available. Check your installation.")

def check_cudnn():
    print("\n🔍 Checking cuDNN Availability...\n")
    print("cuDNN Available:", torch.backends.cudnn.is_available())
    if torch.backends.cudnn.is_available():
        print("cuDNN Version:", torch.backends.cudnn.version())
    else:
        print("❌ cuDNN is NOT available. Ensure it's installed correctly.")

def check_cudnn_files():
    cudnn_path = "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/bin/cudnn64_9.dll"
    print("\n🔍 Checking cuDNN Installation...\n")
    
    if os.path.exists(cudnn_path):
        print(f"✅ cuDNN found at: {cudnn_path}")
    else:
        print("❌ cuDNN DLL not found. Ensure you copied cuDNN files to the CUDA directory.")

def check_whisper_model():
    print("\n🔍 Checking Faster-Whisper Model Loading...\n")

    model_path = "C:/tmp/medium"
    if not os.path.exists(model_path):
        print(f"❌ Model path {model_path} not found! Manually download from Hugging Face and place it there.")
        return

    try:
        print("⏳ Loading Faster-Whisper Model...")
        start_time = time.time()
        model = WhisperModel("medium", download_root=model_path, device="cuda" if torch.cuda.is_available() else "cpu")
        end_time = time.time()
        print(f"✅ Model loaded successfully in {end_time - start_time:.2f} seconds!")
    except Exception as e:
        print("❌ Whisper Model Loading Failed!")
        print(f"Error: {e}")

def main():
    print("\n========================= 🚀 SYSTEM CHECK SCRIPT 🚀 =========================\n")
    check_cuda()
    check_cudnn()
    check_cudnn_files()
    check_whisper_model()
    print("\n✅ Check Complete! If there are errors, follow the recommendations above.")

if __name__ == "__main__":
    main()

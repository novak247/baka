import ctypes

try:
    # You might need to specify the full path if it's not in your LD_LIBRARY_PATH
    cudnn = ctypes.cdll.LoadLibrary("libcudnn.so")
    cudnn.cudnnGetVersion.restype = ctypes.c_size_t
    version = cudnn.cudnnGetVersion()
    print("cuDNN version:", version)
except OSError as e:
    print("cuDNN library not found:", e)

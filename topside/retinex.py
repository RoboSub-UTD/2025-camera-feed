import cv2
import numpy as np
import time

def white_balance(img):
    """GPU-accelerated white balance correction"""
    if img is None or len(img.shape) != 3:
        raise ValueError("Input image must be a valid 3-channel color image.")
    
    # Convert to UMat for GPU processing
    img_umat = cv2.UMat(img)
    b, g, r = cv2.split(img_umat)
    
    # Calculate averages on GPU
    avg_b = cv2.mean(b)[0]
    avg_g = cv2.mean(g)[0]
    avg_r = cv2.mean(r)[0]
    
    # Compute scaling factors
    scale = (avg_g + avg_r + avg_b) / (3 * np.array([avg_b, avg_g, avg_r]))
    
    # Apply scaling on GPU
    b = cv2.multiply(b, float(scale[0]))
    g = cv2.multiply(g, float(scale[1]))
    r = cv2.multiply(r, float(scale[2]))
    
    # Merge back and get result from GPU
    return cv2.merge((b, g, r)).get()

def single_scale_retinex_gpu(img, sigma):
    """GPU-accelerated Single-Scale Retinex"""
    img_float = img.astype(np.float32)
    img_umat = cv2.UMat(img_float)
    
    # Gaussian blur on GPU
    blurred = cv2.GaussianBlur(img_umat, (0, 0), sigma)
    
    # Logarithm operations
    log_img = cv2.log(cv2.add(img_umat, 1.0))
    log_blur = cv2.log(cv2.add(blurred, 1.0))
    
    # Subtract on GPU
    retinex = cv2.subtract(log_img, log_blur)
    return retinex.get()

def multi_scale_retinex_gpu(img, sigmas=[15, 80, 250]):
    """GPU-accelerated Multi-Scale Retinex"""
    retinex = np.zeros_like(img, dtype=np.float32)
    
    for sigma in sigmas:
        retinex += single_scale_retinex_gpu(img, sigma)
    
    return retinex / len(sigmas)

def underwater_retinex_gpu(img):
    """Optimized underwater Retinex with GPU acceleration"""
    # White balance on GPU
    img_wb = white_balance(img)
    
    # Convert to float32 for processing
    img_float = img_wb.astype(np.float32)
    
    # MSR on GPU
    retinex = multi_scale_retinex_gpu(img_float)
    
    # Normalization on CPU (faster for this operation)
    min_val = np.min(retinex)
    max_val = np.max(retinex)
    retinex = (retinex - min_val) / (max_val - min_val) * 255
    retinex = np.uint8(retinex)
    
    # Bilateral filter on GPU
    retinex_umat = cv2.UMat(retinex)
    retinex_filtered = cv2.bilateralFilter(retinex_umat, 9, 75, 75)
    return retinex_filtered.get()

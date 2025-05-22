import cv2
import numpy as np

# Checks if CUDA is available
def is_cuda_available():
    return cv2.cuda.getCudaEnabledDeviceCount() > 0

def white_balance(img):
    """GPU-accelerated white balance correction with CUDA or OpenCL"""
    if img is None or len(img.shape) != 3:
        raise ValueError("Input image must be a valid 3-channel color image.")
    
    if is_cuda_available():
        img_gpu = cv2.cuda_GpuMat()
        img_gpu.upload(img)
        bgr = cv2.cuda.split(img_gpu)
        avg_b = cv2.cuda.mean(bgr[0])[0]
        avg_g = cv2.cuda.mean(bgr[1])[0]
        avg_r = cv2.cuda.mean(bgr[2])[0]
        scale = (avg_g + avg_r + avg_b) / (3 * np.array([avg_b, avg_g, avg_r]))
        b = cv2.cuda.multiply(bgr[0], scale[0])
        g = cv2.cuda.multiply(bgr[1], scale[1])
        r = cv2.cuda.multiply(bgr[2], scale[2])
        merged = cv2.cuda.merge((b, g, r))
        return merged.download()
    
    else:

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
    """GPU-accelerated Single-Scale Retinex with CUDA or OpenCL"""
    img_float = img.astype(np.float32)
    if is_cuda_available():
        img_gpu = cv2.cuda_GpuMat()
        img_gpu.upload(img_float)
        blurred = cv2.cuda.createGaussianFilter(img_gpu.type(), img_gpu.type(), (0, 0), sigma).apply(img_gpu)
        log_img = cv2.cuda.log(cv2.cuda.add(img_gpu, 1.0))
        log_blur = cv2.cuda.log(cv2.cuda.add(blurred, 1.0))
        retinex = cv2.cuda.subtract(log_img, log_blur)
        return retinex.download()
    else:
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

    if is_cuda_available():
        retinex_gpu = cv2.cuda_GpuMat()
        retinex_gpu.upload(retinex)
        retinex_norm = cv2.cuda.normalize(retinex_gpu, None, 0, 255, cv2.NORM_MINMAX)
        retinex_norm = cv2.cuda.convertTo(retinex_norm, cv2.CV_8U)

        retinex_norm_cpu = retinex_norm.download()
        retinex_filtered = cv2.bilateralFilter(retinex_norm_cpu, 9, 75, 75)
        return retinex_filtered
    else:
    
        # Normalization and bilateral filter on GPU
        retinex_umat = cv2.UMat(retinex)
        retinex_norm = cv2.normalize(retinex_umat, None, 0, 255, cv2.NORM_MINMAX)
        retinex_norm = cv2.convertScaleAbs(retinex_norm)
        retinex_filtered = cv2.bilateralFilter(retinex_norm, 9, 75, 75)
        return retinex_filtered.get()

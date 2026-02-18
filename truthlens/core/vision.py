import cv2
import numpy as np

def analyze_image(image_bytes):
    """
    Performs basic image analysis using OpenCV.
    Returns a dictionary of image metrics.
    """
    if not image_bytes:
        return {"has_image": False, "quality_score": 0}

    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
             return {"has_image": False, "error": "Invalid image format"}

        # Basic metrics
        height, width, channels = img.shape
        resolution = width * height
        
        # Blur detection (Laplacian variance)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = laplacian_var < 100 # Threshold
        
        # Brightness
        brightness = np.mean(gray)
        
        quality_score = 0
        if not is_blurry: quality_score += 4
        if resolution > 1000000: quality_score += 3 # > 1MP
        if 50 < brightness < 200: quality_score += 3 # Good exposure
        
        return {
            "has_image": True,
            "resolution": f"{width}x{height}",
            "is_blurry": is_blurry,
            "brightness": round(brightness, 2),
            "quality_score": min(10, quality_score)
        }

    except Exception as e:
        return {"has_image": False, "error": str(e)}

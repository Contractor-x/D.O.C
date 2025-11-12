"""
Image Preprocessing for OCR
Enhances drug images for better text extraction.
"""

import logging
from typing import Tuple
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Handles image preprocessing for OCR operations."""

    def __init__(self):
        self.target_size = (800, 600)  # Optimal size for OCR

    def preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Apply comprehensive preprocessing to optimize image for OCR.

        Args:
            image: PIL Image to preprocess

        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Apply preprocessing steps
            processed = self._resize_image(opencv_image)
            processed = self._convert_to_grayscale(processed)
            processed = self._enhance_contrast(processed)
            processed = self._reduce_noise(processed)
            processed = self._sharpen_image(processed)
            processed = self._correct_skew(processed)

            # Convert back to PIL
            processed_pil = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))

            return processed_pil

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image  # Return original if preprocessing fails

    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image to optimal dimensions for OCR."""
        height, width = image.shape[:2]

        # Calculate scaling factor to fit within target size while maintaining aspect ratio
        scale = min(self.target_size[0] / width, self.target_size[1] / height)

        if scale < 1:  # Only resize if image is larger than target
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            return resized

        return image

    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale."""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE."""
        if len(image.shape) == 3:
            # Convert to LAB color space for better contrast enhancement
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            # Merge channels
            lab = cv2.merge([l, a, b])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # Grayscale image
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            return clahe.apply(image)

    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """Reduce noise while preserving text edges."""
        # Apply bilateral filter to reduce noise while keeping edges sharp
        return cv2.bilateralFilter(image, 9, 75, 75)

    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Sharpen the image to make text clearer."""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)

    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Correct text skew in the image.
        This is a simplified version - production systems might use more sophisticated methods.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Threshold the image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return image

        # Find the largest contour (likely the main text area)
        largest_contour = max(contours, key=cv2.contourArea)

        # Get minimum area rectangle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]

        # Correct angle if it's significantly skewed
        if abs(angle) > 5 and abs(angle) < 85:
            # Rotate the image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)

            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REPLICATE)
            return rotated

        return image

    def preprocess_for_barcode(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image specifically for barcode/NDC detection.

        Args:
            image: PIL Image to preprocess

        Returns:
            Preprocessed PIL Image optimized for barcode detection
        """
        try:
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Resize for barcode detection (barcodes need higher resolution)
            height, width = opencv_image.shape[:2]
            scale = 1000 / max(width, height)
            if scale > 1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                opencv_image = cv2.resize(opencv_image, (new_width, new_height),
                                        interpolation=cv2.INTER_CUBIC)

            # Convert to grayscale
            if len(opencv_image.shape) == 3:
                gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = opencv_image

            # Enhance contrast for barcode detection
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Apply slight blur to reduce noise
            blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

            # Convert back to PIL
            processed_pil = Image.fromarray(blurred)

            return processed_pil

        except Exception as e:
            logger.error(f"Barcode preprocessing failed: {e}")
            return image

    def detect_text_regions(self, image: Image.Image) -> list:
        """
        Detect regions containing text in the image.

        Args:
            image: PIL Image to analyze

        Returns:
            List of bounding boxes for text regions
        """
        try:
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)

            # Apply threshold to get binary image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            text_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small contours
                    x, y, w, h = cv2.boundingRect(contour)
                    # Filter based on aspect ratio (text is usually wider than tall)
                    if w > h and w > 20:
                        text_regions.append((x, y, w, h))

            return text_regions

        except Exception as e:
            logger.error(f"Text region detection failed: {e}")
            return []

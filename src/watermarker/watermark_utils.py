from PIL.Image import Image

from src.watermarker.enum import WatermarkPosition

def adjust_opacity(image: Image, opacity: float) -> Image:
    """
    Adjust the opacity of an image.

    Args:
        image (Image.Image): The input image.
        opacity (float): The desired opacity, ranging from 0.0 (transparent) to 1.0 (opaque).

    Returns:
        Image.Image: The image with adjusted opacity.
    """
    # Ensure the image has an alpha channel
    image: Image = image.convert("RGBA")

    # Extract the alpha channel
    alpha = image.split()[3]

    # Adjust the opacity
    alpha = alpha.point(lambda p: p * opacity)

    # Apply the adjusted alpha channel to the image
    image.putalpha(alpha)
    return image


def calculate_position(
        target_image: Image,
        watermark_image: Image,
        position: WatermarkPosition,
        padding: int,
) -> tuple[int, int]:
    """Calculate the position to place the watermark on the target image.

    Args:
        target_image: The target image.
        watermark_image: The watermark image.
        position: The desired position for the watermark.
        padding: Padding around the watermark.

    Returns:
        tuple: (x, y) coordinates for the watermark.
    """
    match position:
        case WatermarkPosition.BOTTOM_RIGHT:
            return (
                max(0, target_image.width - watermark_image.width - padding),
                max(0, target_image.height - watermark_image.height - padding),
            )
        case WatermarkPosition.BOTTOM_LEFT:
            return (
                padding,
                max(0, target_image.height - watermark_image.height - padding),
            )
        case WatermarkPosition.TOP_RIGHT:
            return (
                max(0, target_image.width - watermark_image.width - padding),
                padding,
            )
        case WatermarkPosition.TOP_LEFT:
            return (padding, padding)
        case WatermarkPosition.CENTER:
            return (
                (target_image.width - watermark_image.width) // 2,
                (target_image.height - watermark_image.height) // 2,
            )
        case _:
            raise ValueError(f"Position {position} is not supported.")


from PIL.Image import Image
from PIL.Image import Resampling
from PIL import Image as PILImage

from src.watermarker.enums import WatermarkPosition


def adjust_opacity(
    image: Image, opacity: float, color: tuple[int, int, int] | None = None
) -> Image:
    """
    Adjust the opacity and optionally tint the watermark image.

    Args:
        image (Image.Image): The input image.
        opacity (float): Desired opacity (0.0 to 1.0).
        color (Optional[tuple[int, int, int]]): RGB tint to apply.

    Returns:
        Image.Image: The adjusted watermark image.
    """
    image_rgba: Image = image.convert("RGBA")

    if color is not None:
        r, g, b, alpha = image_rgba.split()
        solid_color = PILImage.new("RGBA", image_rgba.size, color + (0,))
        solid_color.putalpha(alpha)
        image_rgba = solid_color

    r, g, b, a = image_rgba.split()
    a = a.point(lambda p: int(p * opacity))
    image_rgba.putalpha(a)

    return image_rgba


def scale_watermark(
    target_image: Image,
    watermark_image: Image,
    scale_ratio: float = 0.1,
) -> Image:
    """Scale the watermark based on the **shorter side** of target image."""

    target_width, target_height = target_image.size
    short_side = min(target_width, target_height)

    watermark_original_width, watermark_original_height = watermark_image.size

    # Calculate target watermark width based on short side
    target_watermark_width = int(short_side * scale_ratio)

    # Maintain aspect ratio
    scaling_factor = target_watermark_width / watermark_original_width
    target_watermark_height = int(watermark_original_height * scaling_factor)

    # Resize the watermark
    resized_watermark = watermark_image.resize(
        (target_watermark_width, target_watermark_height), resample=Resampling.LANCZOS
    )

    return resized_watermark


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

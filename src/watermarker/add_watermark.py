from enum import StrEnum
from functools import lru_cache
from typing import Final

import click
from pathlib import Path
from PIL import Image, ImageEnhance

from src.watermarker.click_enum_choice import EnumChoice

# TODO:THS:2024-12-02: Add

WM_OPACITY: Final[float] = 1.0
"""Opacity of the watermark applied to a image."""

WM_DEFAULT_PADDING: Final[int] = 20
"""Default padding in pixels."""


class WatermarkPosition(StrEnum):
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM_LEFT = "bottom-left"
    TOP_RIGHT = "top-right"
    TOP_LEFT = "top-left"
    CENTER = "center"


def validate_image_and_watermark(
    target_image: Image.Image,
    watermark_image: Image.Image,
    padding: int = WM_DEFAULT_PADDING,
) -> bool:
    """Validate that the target image is large enough to accommodate the watermark and padding.

    Args:
        target_image: The target image.
        watermark_image: The watermark image.
        padding: The padding to consider around the watermark.

    Returns:
        bool: True if the target image is valid; False otherwise.
    """
    if (
        target_image.width < watermark_image.width + 2 * padding
        or target_image.height < watermark_image.height + 2 * padding
    ):
        return False
    return True


def calculate_position(
    target_image: Image.Image,
    watermark_image: Image.Image,
    position: WatermarkPosition,
    padding: int = WM_DEFAULT_PADDING,
) -> tuple[int, int]:
    """
    Calculate the position to place the watermark on the target image.

    Args:
        target_image (Image.Image): The target image.
        watermark_image (Image.Image): The watermark image.
        position (WatermarkPosition): The desired position for the watermark.
        padding (int): Padding around the watermark.

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
            # Default to bottom-right if an invalid position is provided
            return (
                max(0, target_image.width - watermark_image.width - padding),
                max(0, target_image.height - watermark_image.height - padding),
            )


# Cache the watermark image with adjusted opacity
@lru_cache(maxsize=1)
def load_cached_watermark(watermark_path: Path, opacity: float) -> Image.Image:
    """Load and cache the watermark image with the specified opacity.

    Args:
        watermark_path (Path): Path to the watermark image.
        opacity (float): Desired opacity of the watermark.

    Returns:
        Image.Image: The processed watermark image with adjusted opacity.
    """
    watermark_image = Image.open(watermark_path)
    return adjust_opacity(image=watermark_image, opacity=opacity)


def adjust_opacity(image: Image.Image, opacity: float) -> Image.Image:
    """
    Adjust the opacity of an image.

    Args:
        image (Image.Image): The input image.
        opacity (float): The desired opacity, ranging from 0.0 (transparent) to 1.0 (opaque).

    Returns:
        Image.Image: The image with adjusted opacity.
    """
    # Ensure the image has an alpha channel
    image = image.convert("RGBA")

    # Extract the alpha channel
    alpha = image.split()[3]

    # Adjust the opacity
    alpha = alpha.point(lambda p: p * opacity)

    # Apply the adjusted alpha channel to the image
    image.putalpha(alpha)

    return image


def add_watermark(
    target_image_path: Path,
    watermark_image_path: Path,
    output_image_path: Path,
    opacity: float = WM_OPACITY,
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
    padding: int = WM_DEFAULT_PADDING,
) -> None:
    """
    Add a watermark to the target image.

    Args:
        target_image_path: Path to the target image.
        watermark_image_path: Path to the watermark image.
        output_image_path: Path to store the resulting image.
    """
    # Open the target image and the watermark image
    target_image = Image.open(target_image_path)
    watermark_image = load_cached_watermark(watermark_image_path, opacity)

    # TODO: Add padding

    # Validate image and watermark dimensions
    if not validate_image_and_watermark(target_image, watermark_image, padding):
        raise ValueError(
            "The target image is too small to accommodate the watermark and padding."
        )

    # Calculate the position for the watermark
    watermark_position = calculate_position(
        target_image=target_image,
        watermark_image=watermark_image,
        position=position,
        padding=padding,
    )

    # Blend the watermark image with the target image using alpha blending
    target_image.paste(watermark_image, watermark_position, mask=watermark_image)

    # Save the resulting image
    target_image.save(output_image_path)


@click.command()
@click.argument("target_image_path", type=click.Path(exists=True, path_type=Path))
@click.argument("watermark_image_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_image_path", type=click.Path(path_type=Path))
@click.option(
    "--opacity",
    type=float,
    default=WM_OPACITY,
    show_default=True,
    help="Opacity of the watermark (0.0 to 1.0).",
)
@click.option(
    "--position",
    type=EnumChoice(WatermarkPosition),
    default=WatermarkPosition.BOTTOM_RIGHT.value,
    help=(
        "Position of the watermark on the image. Determines its alignment relative to "
        "the image frame. Distance from edges is controlled by the padding value. "
        "Ignored when the position is set to 'center'."
    ),
    show_default=True,
)
@click.option("--padding", type=int, default=WM_DEFAULT_PADDING, show_default=True)
def main(
    target_image_path: Path,
    watermark_image_path: Path,
    output_image_path: Path,
    opacity: float,
    position: WatermarkPosition,
    padding: int,
) -> None:
    """Add a watermark to an image.

    Args:
        target_image_path: Path to the target image.
        watermark_image_path: Path to the watermark image.
        output_image_path: Path to store the resulting image.
    """
    try:
        add_watermark(
            target_image_path=target_image_path,
            watermark_image_path=watermark_image_path,
            output_image_path=output_image_path,
            opacity=opacity,
            position=position,
            padding=padding,
        )
    except ValueError as error:
        click.echo(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()

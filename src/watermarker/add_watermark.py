from functools import lru_cache
from typing import Final

import click
from pathlib import Path
from PIL import Image

from src.watermarker.click_enum_choice import EnumChoice
from src.watermarker.enum import WatermarkPosition
from src.watermarker.watermark_utils import adjust_opacity, calculate_position

DEFAULT_OPACITY: Final[float] = 1.0
"""Opacity of the watermark applied to a image."""

DEFAULT_PADDING: Final[int] = 20
"""Default padding in pixels."""

DEFAULT_POSITION: Final[WatermarkPosition] = WatermarkPosition.BOTTOM_RIGHT
"""Default watermark position on the image."""


def validate_image_and_watermark(
    target_image: Image.Image,
    watermark_image: Image.Image,
    padding: int = DEFAULT_PADDING,
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


def add_watermark(
    target_image_path: Path,
    watermark_image_path: Path,
    output_image_path: Path,
    opacity: float = DEFAULT_OPACITY,
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
    padding: int = DEFAULT_PADDING,
) -> None:
    """Add a watermark to the target image.

    Args:
        target_image_path: Path to the target image.
        watermark_image_path: Path to the watermark image.
        output_image_path: Path to store the resulting image.
        opacity: The opacity level of the watermark. Must be a float
                 between 0 (completely transparent) and 1 (completely opaque).
        position: The position of the watermark on the target image.
                  Defaults to `WatermarkPosition.BOTTOM_RIGHT`.
        padding: The padding (in pixels) between the watermark and the
                 edges of the target image.
    """
    target_image: Image.Image = Image.open(target_image_path)
    watermark_image: Image.Image = load_cached_watermark(watermark_image_path, opacity)

    # Validate image and watermark dimensions
    if not validate_image_and_watermark(target_image, watermark_image, padding):
        raise ValueError(
            "The target image is too small to accommodate the watermark and padding."
        )

    if opacity > 1.0 or opacity < 0.0:
        raise ValueError(f"Opacity value {opacity} is invalid.")

    # Calculate the position for the watermark
    position_x_y: tuple[int, int] = calculate_position(
        target_image=target_image,
        watermark_image=watermark_image,
        position=position,
        padding=padding,
    )

    # Blend the watermark image with the target image using alpha blending
    target_image.paste(watermark_image, position_x_y, mask=watermark_image)
    target_image.save(output_image_path)


@click.command()
@click.argument("target_image_path", type=click.Path(exists=True, path_type=Path))
@click.argument("watermark_image_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_image_path", type=click.Path(path_type=Path))
@click.option(
    "--opacity",
    type=float,
    default=DEFAULT_OPACITY,
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
@click.option("--padding", type=int, default=DEFAULT_PADDING, show_default=True)
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
        opacity: The opacity level of the watermark. Must be a float
                 between 0 (completely transparent) and 1 (completely opaque).
        position: The position of the watermark on the target image.
                  Defaults to `WatermarkPosition.BOTTOM_RIGHT`.
        padding: The padding (in pixels) between the watermark and the
                 edges of the target image.
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


if __name__ == "__main__":
    main()

from functools import lru_cache
from typing import Final

import click
from pathlib import Path
from PIL import Image

from src.watermarker.click_enum_choice import EnumChoice
from src.watermarker.enums import WatermarkPosition
from src.watermarker.watermark_utils import (
    adjust_opacity,
    calculate_position,
    scale_watermark,
)

DEFAULT_OPACITY: Final[float] = 1.0
"""Opacity of the watermark applied to a image."""

DEFAULT_PADDING: Final[int] = 20
"""Default padding in pixels."""

DEFAULT_POSITION: Final[WatermarkPosition] = WatermarkPosition.BOTTOM_RIGHT
"""Default watermark position on the image."""

DEFAULT_WATERMARK_SCALE_RATIO = 0.1


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
def load_cached_watermark(
    watermark_path: Path, opacity: float, color: tuple[int, int, int] | None = None
) -> Image.Image:
    """Load and cache the watermark image with the specified opacity.

    Args:
        watermark_path (Path): Path to the watermark image.
        opacity (float): Desired opacity of the watermark.

    Returns:
        Image.Image: The processed watermark image with adjusted opacity.
    """
    watermark_image = Image.open(watermark_path)
    return adjust_opacity(image=watermark_image, opacity=opacity, color=color)


def add_watermark(
    target_image_path: Path,
    watermark_image_path: Path,
    output_image_path: Path,
    opacity: float = DEFAULT_OPACITY,
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
    padding: int = DEFAULT_PADDING,
    watermark_scale_ratio: float = DEFAULT_WATERMARK_SCALE_RATIO,
    color: tuple[int, int, int] | None = None,
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
    watermark_image: Image.Image = load_cached_watermark(
        watermark_image_path, opacity, color
    )

    # Validate image and watermark dimensions
    if not validate_image_and_watermark(target_image, watermark_image, padding):
        raise ValueError(
            "The target image is too small to accommodate the watermark and padding."
        )

    if opacity > 1.0 or opacity < 0.0:
        raise ValueError(f"Opacity value {opacity} is invalid.")

    # Scale the watermark
    watermark_image = scale_watermark(
        target_image, watermark_image, scale_ratio=watermark_scale_ratio
    )

    # Calculate the position for the watermark
    position_x_y: tuple[int, int] = calculate_position(
        target_image=target_image,
        watermark_image=watermark_image,
        position=position,
        padding=padding,
    )

    # Blend the watermark image with the target image using alpha blending
    exif_data = target_image.info.get("exif")
    target_image.paste(watermark_image, position_x_y, mask=watermark_image)

    if exif_data:
        target_image.save(output_image_path, exif=exif_data)
    else:
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
@click.option(
    "--color",
    type=str,
    default=None,
    help="Optional RGB color tint, e.g. '255,0,0' for red.",
)
def main(
    target_image_path: Path,
    watermark_image_path: Path,
    output_image_path: Path,
    opacity: float,
    position: WatermarkPosition,
    padding: int,
    color: str | None = None,
) -> None:
    """Add a watermark to an image.

    Args:
        target_image_path: Path to the target image or Folder.
        watermark_image_path: Path to the watermark image.
        output_image_path: Path to store the resulting image, can be file or folder.
        opacity: The opacity level of the watermark. Must be a float
                 between 0 (completely transparent) and 1 (completely opaque).
        position: The position of the watermark on the target image.
                  Defaults to `WatermarkPosition.BOTTOM_RIGHT`.
        padding: The padding (in pixels) between the watermark and the
                 edges of the target image.
    """

    color_tuple = None
    if color:
        try:
            color_tuple = tuple(map(int, color.split(",")))
            if len(color_tuple) != 3 or not all(0 <= c <= 255 for c in color_tuple):
                raise ValueError()
        except Exception:
            raise click.BadParameter(
                "Color must be in the format R,G,B with values between 0 and 255."
            )

    # TODO: validate path inputs, if working with folders, ensure output path is a folder etc.
    if target_image_path.is_dir():
        for image_path in target_image_path.glob("*"):
            watermarked_output_image_path = (
                output_image_path / f"watermarked_{image_path.name}"
            )
            try:
                add_watermark(
                    target_image_path=image_path,
                    watermark_image_path=watermark_image_path,
                    output_image_path=watermarked_output_image_path,
                    opacity=opacity,
                    position=position,
                    padding=padding,
                    watermark_scale_ratio=DEFAULT_WATERMARK_SCALE_RATIO,
                    color=color_tuple,
                )
                click.echo(f"Watermark added to {image_path.name}")
            except ValueError as error:
                click.echo(f"Error processing {image_path.name}: {error}")
    else:
        try:
            add_watermark(
                target_image_path=target_image_path,
                watermark_image_path=watermark_image_path,
                output_image_path=output_image_path,
                opacity=opacity,
                position=position,
                padding=padding,
                watermark_scale_ratio=DEFAULT_WATERMARK_SCALE_RATIO,
                color=color_tuple,
            )
        except ValueError as error:
            click.echo(f"Error: {error}")


if __name__ == "__main__":
    main()

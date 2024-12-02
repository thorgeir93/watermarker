from typing import Final

import click
from pathlib import Path
from PIL import Image, ImageEnhance

# TODO:THS:2024-12-02: Add

WM_OPACITY: Final[float] = 1.0
"""Opacity of the watermark applied to a image."""


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
    watermark_image = Image.open(watermark_image_path)

    # Adjust the opacity of the watermark image
    watermark_image = adjust_opacity(image=watermark_image, opacity=opacity)

    # Resize the watermark image if needed
    # You can adjust the size as per your requirements
    # watermark_image = watermark_image.resize((200, 200))

    # Define the position where the watermark will be placed
    # Adjust the values to change the position
    # position = (target_image.width - watermark_image.width - 10, target_image.height - watermark_image.height - 10)
    position = (40, target_image.height - watermark_image.height - 250)

    # Blend the watermark image with the target image using alpha blending
    target_image.paste(watermark_image, position, mask=watermark_image)

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
def main(
    target_image_path: Path,
    watermark_image_path: Path,
    output_image_path: Path,
    opacity: float,
) -> None:
    """
    Add a watermark to an image.

    Args:
        target_image_path: Path to the target image.
        watermark_image_path: Path to the watermark image.
        output_image_path: Path to store the resulting image.
    """
    add_watermark(
        target_image_path=target_image_path,
        watermark_image_path=watermark_image_path,
        output_image_path=output_image_path,
        opacity=opacity,
    )


if __name__ == "__main__":
    main()

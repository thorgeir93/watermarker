import os
from pathlib import Path
import click
from add_watermark import add_watermark


@click.command()
@click.argument('target_directory', type=click.Path(exists=True))
@click.argument('watermark_path', type=click.Path(exists=True))
@click.argument('output_directory', type=click.Path())
def apply_watermark_to_images(target_directory: str, watermark_path: str, output_directory: str) -> None:
    """
    Apply a watermark to a directory of images.

    Args:
        target_directory (str): Path to the directory containing the target images.
        watermark_path (str): Path to the watermark image.
        output_directory (str): Path to store the resulting watermarked images.
    """
    target_directory = Path(target_directory)
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    for file in target_directory.glob("*.jpg"):
        output_path = output_directory / file.name
        add_watermark(str(file), watermark_path, str(output_path))


if __name__ == "__main__":
    apply_watermark_to_images()

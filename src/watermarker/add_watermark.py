import click
from pathlib import Path
from PIL import Image, ImageEnhance


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

def add_watermark(target_image_path: str, watermark_image_path: str, output_image_path: str) -> None:
    """
    Add a watermark to the target image.

    Args:
        target_image_path (str): Path to the target image.
        watermark_image_path (str): Path to the watermark image.
        output_image_path (str): Path to store the resulting image.
    """
    # Open the target image and the watermark image
    target_image = Image.open(target_image_path)
    watermark_image = Image.open(watermark_image_path)

    # Adjust the opacity of the watermark image
    watermark_image = adjust_opacity(watermark_image, 0.5)  # Set opacity to 50%


    # Resize the watermark image if needed
    # You can adjust the size as per your requirements
    #watermark_image = watermark_image.resize((200, 200))

    # Define the position where the watermark will be placed
    # Adjust the values to change the position
    position = (target_image.width - watermark_image.width - 10, target_image.height - watermark_image.height - 10)

    # Blend the watermark image with the target image using alpha blending
    target_image.paste(watermark_image, position, mask=watermark_image)

    # Save the resulting image
    target_image.save(output_image_path)


@click.command()
@click.argument('target_image_path', type=click.Path(exists=True))
@click.argument('watermark_image_path', type=click.Path(exists=True))
@click.argument('output_image_path', type=click.Path())
def main(target_image_path: str, watermark_image_path: str, output_image_path: str) -> None:
    """
    Add a watermark to an image.

    Args:
        target_image_path (str): Path to the target image.
        watermark_image_path (str): Path to the watermark image.
        output_image_path (str): Path to store the resulting image.
    """
    target_image_path = Path(target_image_path)
    watermark_image_path = Path(watermark_image_path)
    output_image_path = Path(output_image_path)

    add_watermark(target_image_path, watermark_image_path, output_image_path)


if __name__ == '__main__':
    main()

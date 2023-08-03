# Apply Watermark to Images

This script allows you to apply a watermark to a directory of images or on a single image.

## Prerequisites

- Python 3.6 or above
- Poetry package manager

## Installation

1. Clone the repository or copy the script files to your desired location.

2. Open a terminal or command prompt.

3. Navigate to the directory where the script files are located.

4. Run the following command to install the dependencies using Poetry:

```
poetry install
```

## Usage

1. Open a terminal or command prompt.

2. Navigate to the directory where the script files are located.

3. Run the script using the following command:

```
poetry run python src/watermarker/watermarker.py <target_directory> <watermark_path> <output_directory>
```

   Replace `<target_directory>` with the path to the directory containing the target images.

   Replace `<watermark_path>` with the path to the watermark image.

   Replace `<output_directory>` with the path to the output directory where the watermarked images will be saved.

4. The script will process each image in the target directory, apply the watermark, and save the watermarked images to the specified output directory.

5. After the script finishes running, check the output directory for the watermarked images.

Make sure to replace `<target_directory>`, `<watermark_path>`, and `<output_directory>` in the command with the appropriate paths for your use case.

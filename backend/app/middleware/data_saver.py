from PIL import Image
import os

def compress_image(input_path, output_path, quality=5):
    image = Image.open(input_path)
    image.save(output_path, "JPEG", quality=quality)

if __name__ == '__main__':
    input_file = 'input_image.jpg'  # Replace with your input image path
    output_file = 'compressed_image.jpg'  # Replace with your desired output path
    compress_image(input_file, output_file)

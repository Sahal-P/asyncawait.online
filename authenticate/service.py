from io import BytesIO
from PIL import Image, ImageFile
# import magic
from django.core.files.uploadedfile import InMemoryUploadedFile
# import numpy as np
import sys

ImageFile.LOAD_TRUNCATED_IMAGES = True


def compres_profile_picture(data):
        try:
            image_format = "jpeg" 
            img = Image.open(data["profile_picture"])
            output = BytesIO()
            # Gradient image with a sharp color boundary across the diagonal
            # large_arr = np.fromfunction(lambda x, y, z: (x+y)//(z+1),(256, 256, 3)).astype(np.uint8)
            # large_img = Image.fromarray(large_arr)
            if img.format == "GIF":
                image_format="gif"

            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            img.save(output, format=image_format.upper(), quality=80)

            output.seek(0)
            image = InMemoryUploadedFile(output, 'ImageField', f"{data['profile_picture'].name.split('.')[0]}.{image_format}", f'image/{image_format}',
                                            sys.getsizeof(output), None)
            data["profile_picture"]=image
        except FileNotFoundError as e:
            # Handle the case when the file is not found
            print(f"File not found: {e}")
        except Image.DecompressionBombError as e:
            # Handle the case when the image decompression fails (e.g., due to a large image)
            print(f"Image decompression error: {e}")
        except Exception as e:
            # Handle other exceptions
            print(f"An unexpected error occurred: {e}")
        return data
    
# def detect_image_format(self,file_data):
    #     mime = magic.Magic()
    #     return mime.from_buffer(file_data)
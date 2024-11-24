import pandas as pd
import requests
import os
from PIL import Image
import urllib.request
import http.cookiejar

def process_csv_file(save_dir,csv_file,width=None,height=None):
    if save_dir is None:
        save_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        # Read the CSV file
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        image_url = row['image_url']
        if(image_name in df.columns):
            image_name =f"{row['image_name']}.jpg"
        else:
            image_name =f"{index}.jpg"


        try:
            response = requests.get(image_url, stream=True)

            response.raise_for_status()

            with open(os.path.join(save_dir, image_name), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            if(width is not None & height is not None):
                with Image.open(os.path.join(save_dir, image_name)) as img:
                    resized_img=img.resize((width,height))
                    resized_img.save(os.path.join(save_dir, image_name))

            print(f"Downloaded {image_name}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_url}: {e} ,\n change the image url or provide a jpg file")
        except Exception as e:
            print(f"error downloading {image_name} , {image_url} ,\n change the image url or provide a jpg file")


def download_image(img_url,img_name=None, file_path=None, width=None, height=None):
    if file_path is None:
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        if img_name is None:
            file_name = os.path.basename(img_url)
            file_path = os.path.join(downloads_folder, file_name)
        else:
            file_path = os.path.join(downloads_folder, img_name)
    else:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        # Set up custom headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        req = urllib.request.Request(img_url, headers=headers)

        # Download the image
        try:
            with urllib.request.urlopen(req) as response:
                with open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
            print(f"Downloaded image to {file_path}")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            return
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return

        # Open and resize the image if width and height are provided
        if width is not None and height is not None:
            try:
                with Image.open(file_path) as img:
                    resized_img = img.resize((width, height))
                    resized_img.save(file_path, format=img.format)  # Save with the same format as the original
                    print(f"Resized image to {width}x{height}")
            except IOError:
                print("The downloaded file is not a valid image.")
    except Exception as e:
        print(f"An error occurred: {e}")


# # # Example usage:
# if __name__ == "__main__":
#     imge_url="https://w0.peakpx.com/wallpaper/85/708/HD-wallpaper-background-abstract-jpg-colors-pretty-fun-thumbnail.jpg"
#     image_name="seller.jpg"
#     save_Dir=f"D:/Downloads/{image_name}"
#     download_images_via_url(img_url=imge_url,file_path=save_Dir,width=500,height=500)
#     csv_file = ''
#     save_directory = 'downloaded_images'
#     resized_width=500
#     resized_height=500
#     download_images_from_csv(csv_file, save_directory,resized_width,resized_height)
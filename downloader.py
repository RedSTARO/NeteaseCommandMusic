import os

def check_and_download_folder(folder_name):
    folder_path = os.path.join(os.getcwd(), folder_name)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        if not is_folder_empty(folder_path):
            print(f"Folder '{folder_name}' already exists and is not empty. Skipping...")
            return
        else:
            print(f"Folder '{folder_name}' already exists but is empty. Downloading...")
            downloader(folder_path)
    else:
        os.mkdir(folder_path)
        print(f"Created folder '{folder_name}'. Downloading...")
        downloader(folder_path)

def is_folder_empty(folder_path):
    return len(os.listdir(folder_path)) == 0

def downloader(folder_path):
    # 在这里执行下载操作
    print(f"Downloading files to folder '{folder_path}'")

# def downloader(URL, file):
#     file = songPath + file
#     response = requests.get(URL, stream=True)
#     with open(file, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=1024):
#             if chunk:
#                 file.write(chunk)


# 例子使用
folder_name = "example_folder"
check_and_download_folder(folder_name)

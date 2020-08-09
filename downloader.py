import os

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from tqdm import tqdm

DATA_DIR = 'data'
DRIVE_ROOT_ID = '0BzsdkU4jWx9Ba2x1NTZhdzQ5Zjg'

FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

drive = None

class DriveFolder:
    def __init__(self, folder_metadata, parent=None):
        self.id = folder_metadata['id']
        self.path = parent.path if parent is not None else []
        self.path.append(folder_metadata['title'])

    @classmethod
    def from_id(cls, folder_id, root_folder):
        return cls({'id': folder_id, 'title': root_folder})

    @staticmethod
    def is_folder(file_metadata):
        return file_metadata['mimeType'] == FOLDER_MIMETYPE

    def get_path(self):
        return os.path.join(*self.path)

    def get_file_path(self, filename):
        return os.path.join(*self.path, filename)

    def list_folder(self):
        # Fetch directory listing
        file_list = drive.ListFile({'q': f"'{self.id}' in parents and trashed=false"}).GetList()

        # Split by file/folder
        files = [{'id': i['id'], 'name': i['title']} for i in file_list if not DriveFolder.is_folder(i)]
        folders = [DriveFolder(i, self) for i in file_list if DriveFolder.is_folder(i)]

        return (files, folders)


if __name__ == '__main__':
    print("----------- Google Drive Folder Downloader -----------")
    file_cnt = 0

    # Authenticate user
    print("[INFO] Authenticating user...")
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Auto-iterate through all files in the root folder.
    to_download = [DriveFolder.from_id(DRIVE_ROOT_ID, DATA_DIR)]
    while to_download:
        # Fetch folder
        curr_folder = to_download.pop()
        files, subfolders = curr_folder.list_folder()
        to_download.extend(subfolders)

        # Print folder metadata
        print(f"[INFO] Entering folder {curr_folder.get_path()} with {len(files)} files to download")

        # Create folder and begin download
        os.makedirs(curr_folder.get_path())
        file_cnt += len(files)

        for file in tqdm(files):
            gfile = drive.CreateFile({'id': file['id']})
            try:
                gfile.GetContentFile(curr_folder.get_file_path(file['name']))
            except:
                print(f"[ERROR] Failed to download file {file['name']}")

    print(f"[INFO] Completed download of {file_cnt} files")

import argparse
import humanize
import os

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from pydrive.files import ApiRequestError, FileNotUploadedError, FileNotDownloadableError
from tqdm import tqdm

FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

drive = None

class DriveFolder:
    def __init__(self, folder_metadata, parent=None):
        self.id = folder_metadata['id']
        self.path = parent.path if parent is not None else ()
        self.path += (folder_metadata['title'], )

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
        files = [file for file in file_list if not DriveFolder.is_folder(file)]
        folders = [DriveFolder(file, self) for file in file_list if DriveFolder.is_folder(file)]

        return (files, folders)

if __name__ == '__main__':
    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("folder_id", help="ID of the folder to download")
    ap.add_argument("-l", "--location", default="download",
                    help="location to place the download on disk")
    args = ap.parse_args()

    print("----------- Google Drive Folder Downloader -----------")
    file_cnt = 0
    total_size = 0

    # Authenticate user
    print("[INFO] Authenticating user...")
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Auto-iterate through all files in the root folder.
    to_download = [DriveFolder.from_id(args.folder_id, args.location)]
    while to_download:
        # Fetch folder
        curr_folder = to_download.pop()
        files, subfolders = curr_folder.list_folder()
        to_download.extend(subfolders)

        # Print folder metadata
        folder_size = sum(int(file['fileSize']) for file in files if 'fileSize' in file)
        total_size += folder_size
        print(f"[INFO] Entering folder {curr_folder.get_path()} with {len(files)} files to download, totaling {humanize.naturalsize(folder_size)}")

        # Create folder and begin download
        try:
            os.makedirs(curr_folder.get_path())
        except FileExistsError:
            print("[WARNING] This folder already exists! Continuing...")
        file_cnt += len(files)

        for file in tqdm(files):
            gfile = drive.CreateFile({'id': file['id']})
            try:
                gfile.GetContentFile(curr_folder.get_file_path(file['title']))
            except (ApiRequestError, FileNotUploadedError, FileNotDownloadableError):
                print(f"[ERROR] Failed to download file {file['title']}")

    print(f"[INFO] Completed download of {file_cnt} files, totaling {humanize.naturalsize(total_size)}")

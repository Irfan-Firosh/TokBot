import dropbox as dbx
import os
import time
from typing import List

class DropboxUploader:
    def __init__(self, chunk_size_mb=8):

        self.client = dbx.Dropbox(
            app_key=os.getenv("DROPBOX_APP_KEY"),
            app_secret=os.getenv("DROPBOX_APP_SECRET"),
            oauth2_refresh_token=os.getenv("DROPBOX_REFRESH_TOKEN")
        )
        self.folder_path = os.getenv("DROPBOX_ROOT_FOLDER")
        self.chunk_size = chunk_size_mb * 1024 * 1024
    
    def upload_file(self, file_path: str, file_name: str):
        if not self.folder_path.startswith('/'):
            self.folder_path = '/' + self.folder_path
        dropbox_path = self.folder_path.rstrip('/') + '/' + file_name
        file_size = os.path.getsize(file_path)
        
        with open(file_path, "rb") as f:
            if file_size <= self.chunk_size:
                self.client.files_upload(f.read(), dropbox_path, mode=dbx.files.WriteMode('overwrite'))
            else:
                session = self.client.files_upload_session_start(f.read(self.chunk_size))
                cursor = dbx.files.UploadSessionCursor(session_id=session.session_id, offset=f.tell())
                commit = dbx.files.CommitInfo(path=dropbox_path, mode=dbx.files.WriteMode('overwrite'))
                
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= self.chunk_size:
                        self.client.files_upload_session_finish(f.read(self.chunk_size), cursor, commit)
                        break
                    else:
                        self.client.files_upload_session_append_v2(f.read(self.chunk_size), cursor)
                        cursor.offset = f.tell()
    
    def batch_upload_files(self, folder_path: str):
        for file in os.listdir(folder_path):
            self.upload_file(f"{folder_path}/{file}", file)

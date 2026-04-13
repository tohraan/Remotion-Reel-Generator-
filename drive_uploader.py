import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

class DriveUploader:
    """Handles uploading files to Google Drive with specific folder logic."""
    
    def __init__(self, token_path='credentials/token.pickle'):
        self.creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token) # FIXED typo here
        
        if not self.creds:
            raise Exception("❌ Drive credentials not found or invalid. Run reauthorize_drive.py first.")

        # Check if creds are valid
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            
        self.service = build('drive', 'v3', credentials=self.creds)

    def get_or_create_folder(self, folder_name, parent_id=None):
        """Finds a folder by name or creates it if it doesn't exist."""
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        else:
            print(f"📁 Creating folder: {folder_name}")
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')

    def upload_reel(self, file_path, target_root="content-triaxon", target_sub="Reel"):
        """Uploader logic for reels."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"🚀 Preparing to upload {os.path.basename(file_path)} to Drive...")
        
        # 1. Get Root Folder
        root_id = self.get_or_create_folder(target_root)
        
        # 2. Get Subfolder
        sub_id = self.get_or_create_folder(target_sub, parent_id=root_id)
        
        # 3. Upload File
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [sub_id]
        }
        media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        print(f"✅ Upload Complete: {file.get('webViewLink')}")
        return file.get('webViewLink')

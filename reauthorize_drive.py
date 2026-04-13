import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = 'credentials/token.pickle'
    creds_path = 'credentials/credentials.json'

    if os.path.exists(token_path):
        os.remove(token_path)
        print(f"Deleted existing {token_path}")

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save the credentials for the next run
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ Reauthorization successful. Token saved to {token_path}")

if __name__ == '__main__':
    main()

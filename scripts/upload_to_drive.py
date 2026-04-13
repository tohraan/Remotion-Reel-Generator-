import sys
from drive_uploader import DriveUploader

def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_to_drive.py <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        uploader = DriveUploader()
        # Using "Reel" as the subfolder as per previous successful integration
        link = uploader.upload_reel(file_path, target_root="content-triaxon", target_sub="Reel")
        print(f"✅ FINAL_DRIVE_LINK: {link}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

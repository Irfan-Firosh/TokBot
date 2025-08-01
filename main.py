from dotenv import load_dotenv
from helpers.dropboxUploader import DropboxUploader

load_dotenv()


def main():
    dropboxUploader = DropboxUploader()
    file_path = "Most embarassing moments.mp4"
    file_name = "Most embarassing moments.mp4"
    dropboxUploader.upload_file(file_path, file_name)

if __name__ == "__main__":
    main()
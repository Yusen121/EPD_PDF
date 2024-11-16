from pathlib import Path
from log.log import logger


class Finder:

    # EFFECTS: Returns the folder path with the given name within the specified path.
    @staticmethod
    def find_folder(name, path):
        search_path = Path(path)
        # Recursively search for the folder
        for folder in search_path.rglob('*'):
            if folder.is_dir() and folder.name == name:
                return folder
        return None

    # EFFECTS: Returns the md file path with the given name within the specified path.
    @staticmethod
    def find_md_folder(name, path):
        search_path = Path(path)
        # Recursively search for the md file
        for file in search_path.rglob('*.md'):
            if file.is_file() and file.stem == name:
                return file
        return None


if __name__ == "__main__":
    folder_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result/magic-pdf/www.environdec.com:library:epd1347'
    find_folder_path = Finder.find_folder('images', folder_path)
    print(find_folder_path)

    find_md_path = Finder.find_md_folder('www.environdec.com:library:epd1347', folder_path)
    print(find_md_path)

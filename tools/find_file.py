import os
import shutil

class Search:
    @staticmethod
    def find_files(folder_path, file_name):
        """
        Find all files with the specified name in the folder and its subfolders.

        Parameters:
        folder_path (str): The path to the folder to search.
        file_name (str): The name of the file to find.

        Returns:
        list: A list of file paths where the file is found.
        """
        file_paths = []

        for root, dirs, files in os.walk(folder_path):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                file_paths.append(file_path)

        return file_paths

    @staticmethod
    def pick_file_by_id(folder_path, file_name, new_folder_path):
        """
        Load all files and folders with the specified name from the folder and its subfolders,
        and store them in a new path with their original name and a unique number.

        Parameters:
        folder_path (str): The path to the folder containing the file.
        file_name (str): The name of the file or folder to load.
        new_folder_path (str): The path to the folder where the files/folders will be stored.

        Returns:
        list: A list of paths for the stored files/folders.
        """
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        item_paths = []
        item_count = 1

        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                if dir_name == file_name:
                    original_folder_path = os.path.join(root, dir_name)
                    new_folder_name = f"{dir_name}_{item_count}"
                    new_folder_path_with_id = os.path.join(new_folder_path, new_folder_name)

                    try:
                        shutil.copytree(original_folder_path, new_folder_path_with_id)
                        item_paths.append(new_folder_path_with_id)
                        item_count += 1
                    except Exception as e:
                        print(f"An error occurred while copying {original_folder_path}: {e}")

            for file in files:
                if file == file_name:
                    original_file_path = os.path.join(root, file)
                    new_file_name = f"{os.path.splitext(file)[0]}_{item_count}{os.path.splitext(file)[1]}"
                    new_file_path = os.path.join(new_folder_path, new_file_name)

                    try:
                        shutil.copy(original_file_path, new_file_path)
                        item_paths.append(new_file_path)
                        item_count += 1
                    except Exception as e:
                        print(f"An error occurred while copying {original_file_path}: {e}")

        return item_paths


if __name__ == "__main__":
    folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data'
    file_name = 'www.environdec.com:library:epd9869.pdf'
    new_folder = '/Users/apple/PycharmProjects/EPDLibrary/tools/search_output'
    search = Search()
    search.pick_file_by_id(folder_path, file_name, new_folder)
    search.find_files(folder_path, file_name)

    # Todo: /
    # www.environdec.com/library/epd1796.pdf


# import os
# import shutil
#
#
# class Search:
#     @staticmethod
#     def find_files(folder_path, file_name):
#         """
#         Find all files with the specified name in the folder and its subfolders.
#
#         Parameters:
#         folder_path (str): The path to the folder to search.
#         file_name (str): The name of the file to find.
#
#         Returns:
#         list: A list of file paths where the file is found.
#         """
#         file_paths = []
#
#         for root, dirs, files in os.walk(folder_path):
#             if file_name in files:
#                 file_path = os.path.join(root, file_name)
#                 file_paths.append(file_path)
#
#         return file_paths
#
#     @staticmethod
#     def pick_file_by_id(folder_path, file_name, new_folder_path):
#         """
#         Load all JSON files with the specified name from the folder and its subfolders,
#         and store them in a new path with their original name and a unique number.
#
#         Parameters:
#         folder_path (str): The path to the folder containing the file.
#         file_name (str): The name of the file to load.
#         new_folder_path (str): The path to the folder where the files will be stored.
#
#         Returns:
#         list: A list of file paths for the stored files.
#         """
#         if not os.path.exists(new_folder_path):
#             os.makedirs(new_folder_path)
#
#         file_paths = []
#         file_count = 1
#
#         for root, dirs, files in os.walk(folder_path):
#             if file_name in files:
#                 original_file_path = os.path.join(root, file_name)
#                 new_file_name = f"{os.path.splitext(file_name)[0]}_{file_count}{os.path.splitext(file_name)[1]}"
#                 new_file_path = os.path.join(new_folder_path, new_file_name)
#
#                 try:
#                     shutil.copy(original_file_path, new_file_path)
#                     file_paths.append(new_file_path)
#                     file_count += 1
#                 except Exception as e:
#                     print(f"An error occurred while copying {original_file_path}: {e}")
#
#         return file_paths
#
#
# if __name__ == "__main__":
#     folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data'
#     file_name = 'www.environdec.com:library:epd4774.pdf'
#     new_folder = '/Users/apple/PycharmProjects/EPDLibrary/tools/search_output'
#     search = Search()
#     search.pick_file_by_id(folder_path, file_name, new_folder)
#     search.find_files(folder_path, file_name)
#     # search.find_files()
#
#

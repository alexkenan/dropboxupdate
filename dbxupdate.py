"""
Pull the "Updater" folder from Dropbox to update & overwrite folder on RPI
"""
#####################################
#    LAST UPDATED     20 MAY 2017   #
#####################################
import os
import sys
import shutil
import dropbox


def main():
    """
    Main program. Get token, login to dropbox, download folder, overwrite
    :return: None
    """
    path_to_token = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.txt')
    with open(path_to_token) as files:
        token = files.read().strip()

    dbx = dropbox.Dropbox(token)

    if system == 'lin':
        # Get the token since it will always be in the dbxupdate directory

        list_names = get_filenames(dbx)

        for file in list_names:
            if '__pycache__' not in file:
                file1 = file.replace('updater', 'Updater')
                print('Getting {}'.format(file))
                updated_folder_bytes = download_from_dropbox(dbx, file)
                put_in_folder(updated_folder_bytes, file1)

        move_folder(temp_folder + 'Updater/', final_folder)
    else:
        list_dirs = os.listdir('/Users/Alex/Documents/Python3/Updater/')
        for direc in list_dirs:
            if '.DS_Store' not in direc and '__pycache__' not in direc:
                filename = '/Users/Alex/Documents/Python3/Updater/' + direc
                dropbox_filename = '/Updater/' + direc
                with open(filename, 'rb') as f:
                    print('Uploading {}'.format(dropbox_filename))
                    dbx.files_upload(f.read(), dropbox_filename,
                                     mode=dropbox.files.WriteMode('overwrite'))


def put_in_folder(bytes_file, name):
    """
    Put the 
    :param bytes_file: the file as a bytes object
    :param name: Name from the list_of_names
    :return: None
    """
    new_path = temp_folder + name
    new_path = new_path.replace('//', '/')
    open(new_path, 'a').close()
    with open(new_path, 'wb') as f:
        f.write(bytes_file)


def move_folder(path1, path2):
    """
    Move Temp folder from Path1 to Path2 and delete the temp folder
    :param path1: Originiating Path
    :param path2: Destination Path
    :return: None
    """
    tmp_path = path2 + 'Updater/'
    try:
        shutil.rmtree(tmp_path)
    except:
        pass
    shutil.move(path1, path2)


def download_from_dropbox(dropb, path):
    """
    Download folder from dropbox
    :param dropb: dropbox instance
    :param path: str of the file path
    :return: Folder as bytes
    """
    try:
        md, res = dropb.files_download(path)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None

    data = res.content
    return data


def get_filenames(dropb):
    """
    Get all of the files in the Dropbox folder
    :param dropb: dropbox instance
    :return: list of filenames as str
    """
    list_of_files = []
    for filemetadata in dropb.files_list_folder('/Updater').entries:
        list_of_files.append(filemetadata.path_lower)

    return list_of_files


def system_check():
    """
    Make sure all folders are in the right place
    :return: tup of (temp path, final path)
    """
    if sys.platform == 'linux' and 'pi' in os.getcwd():
        try:
            os.mkdir('/home/pi/Dropbox/Updater/')
        except FileExistsError:
            pass
        return '/home/pi/Dropbox/', '/media/pi/USB20FD/', 'lin'
    elif sys.platform == 'darwin':
        try:
            os.mkdir('/Users/Alex/Desktop/dbxTemp/')
            os.mkdir('/Users/Alex/Desktop/dbxTemp/Updater/')
            os.mkdir('/Users/Alex/Desktop/dbxReplace')
        except FileExistsError:
            pass
        return '/Users/Alex/Desktop/dbxTemp/', '/Users/Alex/Desktop/dbxReplace/', 'darwin'

if __name__ == "__main__":
    temp_folder, final_folder, system = system_check()
    main()

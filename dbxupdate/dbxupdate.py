"""
Pull any folder from Dropbox to update & overwrite folder on RPI
"""
#####################################
#    LAST UPDATED     01 JUN 2017   #
#####################################
import os
import sys
from string import capwords
import shutil
import dropbox


def main(pathfolder):
    """
    Main program. Get token, login to dropbox, download folder, overwrite
    :param pathfolder: Folder to copy
    :return: None
    """
    # Get the token since it will always be in the dbxupdate directory
    path_to_token = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.txt')
    with open(path_to_token) as files:
        token = files.read().strip()

    dbx = dropbox.Dropbox(token)

    if system == 'lin':

        os.chdir('/home/pi/')

        list_names = get_filenames(dbx, pathfolder)

        for file in list_names:
            if '__pycache__' not in file:
                if capwords(pathfolder) == pathfolder:
                    file1 = file.replace(pathfolder.lower(), capwords(pathfolder))
                    file1 = file1[1:]
                elif pathfolder[0].isupper() and pathfolder == 'MatchThreader':
                    file1 = file.replace('matchthreader', pathfolder)
                    file1 = file1[1:]
                else:
                    file1 = file[1:]
                print('Getting {}'.format(file))
                updated_folder_bytes = download_from_dropbox(dbx, file)
                put_in_folder(updated_folder_bytes, file1)

        if pathfolder == 'MatchThreader':
            print('Moving MNT.txt and WNT.txt')
            shutil.move('/media/pi/USB20FD/MatchThreader/MNT.txt',
                        '/home/pi/Dropbox/MatchThreader/')
            shutil.move('/media/pi/USB20FD/MatchThreader/WNT.txt',
                        '/home/pi/Dropbox/MatchThreader/')

        move_folder(temp_folder + '{}/'.format(pathfolder), final_folder, pathfolder)
    else:
        if pathfolder == 'MatchThreader':
            list_dirs = os.listdir('/Users/Alex/Documents/Python/MatchThreader/')
            basepath = '/Users/Alex/Documents/Python/'
        else:
            list_dirs = os.listdir('/Users/Alex/Documents/Python3/{}/'.format(pathfolder))
            basepath = '/Users/Alex/Documents/Python3/'
        for direc in list_dirs:
            if '.DS_Store' not in direc and '__pycache__' not in direc and\
                    not direc.endswith('pyc') and not direc.endswith('log'):
                filename = os.path.join(basepath, pathfolder, direc)
                dropbox_filename = os.path.join('/{}/'.format(pathfolder), direc)
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
    if name == 'Matchthreader':
        name = 'MatchThreader'
    try:
        new_path = os.path.join(temp_folder, name)
        open(new_path, 'a').close()
        with open(new_path, 'wb') as f:
            f.write(bytes_file)
    except FileNotFoundError:
        new_path = os.path.join(temp_folder, name.lower())
        open(new_path, 'a').close()
        with open(new_path, 'wb') as f:
            f.write(bytes_file)


def move_folder(path1, path2, pathfolder):
    """
    Move Temp folder from Path1 to Path2 and delete the temp folder
    :param path1: Originiating Path
    :param path2: Destination Path
    :param pathfolder: Either 'Updater' or 'MatchThreader'
    :return: None
    """
    tmp_path = os.path.join(path2, '{}/'.format(pathfolder))
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


def get_filenames(dropb, pathfolder):
    """
    Get all of the files in the Dropbox folder
    :param dropb: dropbox instance
    :param pathfolder: Either 'Updater' or 'MatchThreader'
    :return: list of filenames as str
    """
    list_of_files = []
    for filemetadata in dropb.files_list_folder('/{}'.format(pathfolder)).entries:
        list_of_files.append(filemetadata.path_lower)

    return list_of_files


def system_check(path):
    """
    Make sure all folders are in the right place
    :param path: Either 'Updater' or 'MatchThreader'
    :return: tup of (temp path, final path)
    """
    if sys.platform == 'linux' and 'pi' in os.getcwd():
        try:
            os.mkdir('/home/pi/Dropbox/{}/'.format(path))
        except FileExistsError:
            pass
        return '/home/pi/Dropbox/', '/media/pi/USB20FD/', 'lin'
    elif sys.platform == 'darwin':
        try:
            # os.mkdir('/Users/Alex/Desktop/dbxTemp/')
            # os.mkdir('/Users/Alex/Desktop/dbxTemp/Updater/')
            # os.mkdir('/Users/Alex/Desktop/dbxReplace')
            pass
        except FileExistsError:
            pass
        return '/Users/Alex/Desktop/dbxTemp/', '/Users/Alex/Desktop/dbxReplace/', 'darwin'

if __name__ == "__main__":
    if len(sys.argv) == 2:
        whichfolder = sys.argv[1]
        temp_folder, final_folder, system = system_check(whichfolder)
        main(whichfolder)
    elif len(sys.argv) == 1:
        whichfolder = 'Updater'
        temp_folder, final_folder, system = system_check(whichfolder)
        main(whichfolder)
    else:
        print('Invalid input arguments. Argument must be text and either "Updater" or "MatchThreader"')

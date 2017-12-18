#!/usr/bin/env python3
"""
Pull any folder from Dropbox to update & overwrite folder on RPI
"""
#####################################
#    LAST UPDATED     18 DEC 2017   #
#####################################
import os
import sys
import argparse
from string import capwords
import shutil
import dropbox


def main() -> None:
    """
    Main program
    Get token, login to dropbox, upload/download folder, overwrite
    :return: None
    """
    # Get the token since it will always be in the dbxupdate directory
    path_to_token = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.txt')
    with open(path_to_token) as files:
        token = files.read().strip()

    dbx = dropbox.Dropbox(token)

    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="Folder name to be uploaded or downloaded")
    parser.add_argument("homepath",
                        help="Home path (probably /home/pi/ on RPI or ~/Python3/ on Mac")
    parser.add_argument("finalfolder",
                        help="Final parent folder to move the updated Dropbox folder to")
    parser.add_argument("-push", "--push", action="store_true",
                        help="Push this folder to Dropbox")
    parser.add_argument("-pull", "--pull", action="store_true",
                        help="Pull this folder from Dropbox and overwrite existing")
    args = parser.parse_args()

    temp_folder = os.path.join(args.homepath, 'Dropbox')
    final_folder = args.finalfolder

    if args.pull:
        if os.path.exists(args.homepath):
            # Make sure homepath exists before cd'ing
            os.chdir(args.homepath)
        if not os.path.exists(temp_folder):
            os.mkdir('Dropbox')
            remove_dropbox = True
        else:
            remove_dropbox = False

        list_names = get_filenames(dbx, args.path)

        for file in list_names:
            if '__pycache__' not in file:
                if capwords(args.path) == args.path:
                    # Dealing with 'Updater'
                    file1 = file.replace(args.path.lower(), capwords(args.path))
                    file1 = file1[1:]
                elif args.path[0].isupper() and args.path == 'MatchThreader':
                    # Dealing with MatchThreader
                    file1 = file.replace('matchthreader', args.path)
                    file1 = file1[1:]
                else:
                    # Dealing with all lowercase folder name
                    file1 = file[1:]
                print('Getting {}'.format(file))
                updated_folder_bytes = download_from_dropbox(dbx, file)
                put_in_folder(updated_folder_bytes, file1, temp_folder, args.path)

        if args.path == 'MatchThreader':
            move_rpi_files()

        move_folder(os.path.join(temp_folder, args.path), final_folder, args.path)

        if remove_dropbox:
            if 'Dropbox' in os.getcwd():
                os.chdir('..')

            os.rmdir('Dropbox')

    elif args.push:
        if args.path == 'MatchThreader':
            list_dirs = os.listdir(os.path.join(args.homepath, args.path))
            basepath = args.homepath
        else:
            list_dirs = os.listdir(os.path.join(args.homepath, args.path))
            basepath = args.homepath
        for direc in list_dirs:
            if '.DS_Store' not in direc and '__pycache__' not in direc and\
                    not direc.endswith('pyc') and not direc.endswith('log'):
                filename = os.path.join(basepath, args.path, direc)
                dropbox_filename = os.path.join('/{}/'.format(args.path), direc)
                with open(filename, 'rb') as f:
                    print('Uploading {}'.format(dropbox_filename))
                    dbx.files_upload(f.read(), dropbox_filename,
                                     mode=dropbox.files.WriteMode('overwrite'))
    else:
        raise Exception("You need to specify -push or -pull")


def put_in_folder(bytes_file: bytes, name: str, temp_folder: str, path: str) -> None:
    """
    Put the downloaded file into the correct nested folder
    :param bytes_file: the file as a bytes object
    :param name: Name from the list_of_names
    :param temp_folder: Temporary folder that exists
    :param path: Name of folder being downloaded from Dropbox
    :return: None
    """
    if name.lower() == 'matchthreader':
        name = 'MatchThreader'
        os.chdir('Dropbox')
        os.mkdir('MatchThreader')
    elif name.lower() == 'updater':
        os.chdir('Dropbox')
        os.mkdir('Updater')
        name = "Updater"
    try:
        new_path = os.path.join(temp_folder, name)
        open(new_path, 'w').close()
        with open(new_path, 'wb') as f:
            f.write(bytes_file)
    except FileNotFoundError:
        new_path = os.path.join(temp_folder, name.lower())
        os.chdir('Dropbox')
        os.mkdir(path)
        open(new_path, 'w').close()
        with open(new_path, 'wb') as f:
            f.write(bytes_file)


def move_folder(path1: str, path2: str, pathfolder: str) -> None:
    """
    Move Temp folder from Path1 to Path2 and delete the temp folder
    :param path1: Originiating Path
    :param path2: Destination Path
    :param pathfolder: The name of the folder to be moved
    :return: None
    """
    tmp_path = os.path.join(path2, '{}/'.format(pathfolder))

    try:
        shutil.rmtree(tmp_path)
    except:
        pass

    shutil.move(path1, path2)


def download_from_dropbox(dropb: dropbox, path: str) -> bytes:
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


def move_rpi_files() -> None:
    """
    Do some housekeeping by making sure MNT.txt and WNT.txt are up to date
    :return: None
    """
    if 'pi' in os.getcwd():
        print('Moving MNT.txt and WNT.txt')
        shutil.move('/media/pi/USB20FD/MatchThreader/MNT.txt',
                    '/home/pi/Dropbox/MatchThreader/')
        shutil.move('/media/pi/USB20FD/MatchThreader/WNT.txt',
                    '/home/pi/Dropbox/MatchThreader/')
    else:
        print('Would have moved MNT and WNT files')


def get_filenames(dropb: dropbox, pathfolder: str) -> list:
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


if __name__ == "__main__":
    main()

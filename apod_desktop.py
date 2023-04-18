""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import datetime
import os
import image_lib
import inspect
import sys
import sqlite3
import apod_api
import re
import hashlib

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None  # Full path of image cache database


def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])


def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    date_inp = ''
    date_format = "%Y-%m-%d"
    date_min = datetime(1995, 6, 16)
    date_max = datetime.today()
    if len(sys.argv) >= 2:
        try:
            flag = bool(datetime.strptime(sys.argv[1], date_format))
        except ValueError:
            flag = False
        if flag:
            if datetime.strptime(sys.argv[1], date_format) < date_min:
                print(' input Date can not be an older date than June 16 ,1995 ')
                print('Script execution aborted')
                exit()
            elif datetime.strptime(sys.argv[1], date_format) > date_max:
                print(' APOD date cannot be in the future ')
                print('Script execution aborted')
                exit()
            else:
                date_inp = datetime.strptime(sys.argv[1], date_format)
        else:
            print('Invalid date format;')
            print('Script execution aborted')
            exit()

    else:
        date_inp = datetime.today()

    apod_date_out = datetime.fromisoformat(date_inp.strftime("%Y-%m-%d"))
    return apod_date_out.date()


def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    path_file = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(path_file)


def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db

    # TODO: Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir, 'images')
    print('Image cache directory : ' + image_cache_dir)

    # TODO: Create the image cache directory if it does not already exist
    if os.path.exists(image_cache_dir) is False:
        os.makedirs(image_cache_dir, exist_ok=True)
        print('Image cache directory created.')
    else:
        print('Image cache directory already exists.')

    # TODO: Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

    if os.path.exists(image_cache_db) is False:
        # TODO: Create the DB if it does not already exist
        print('Image cache DB : ' + image_cache_db)
        print('Image cache DB created.')
    else:
        print('Image cache DB already exists.')

    con = sqlite3.connect(image_cache_db)

    cur = con.cursor()

    table_sql = """ CREATE TABLE IF NOT EXISTS APOD ( id INTEGER PRIMARY KEY, APOD_TITLE TEXT NOT NULL, APOD_EXPAIN TEXT NOT NULL, file_path TEXT NOT NULL, SHA256_VAL TEXT NOT NULL  ); """

    cur.execute(table_sql)


def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """

    # TODO: Download the APOD information from the NASA API
    # TODO: Download the APOD image
    # TODO: Check whether the APOD already exists in the image cache
    # TODO: Save the APOD file to the image cache directory
    # TODO: Add the APOD information to the DB

    record_id = 0

    print("APOD date:", apod_date.isoformat())

    # Getting data from API
    apod_data = apod_api.get_apod_info(apod_date)

    apod_title = apod_data['title']

    print('APOD title : ' + apod_title)

    # Getting URL from Image Data
    image_web_url = apod_api.get_apod_image_url(apod_data)

    print('APOD URL : ' + image_web_url)

    # Determining Final Path from image title and URL
    final_path = determine_apod_file_path(apod_title, image_web_url)

    # Downloading Image
    data_image = image_lib.download_image(image_web_url)

    # Calculating Hash Value
    sha_256_val = hashlib.sha256(data_image).hexdigest()

    print('APOD SHA-256 : ' + sha_256_val)

    # Getting Image id from hash value
    img_flag_id = get_apod_id_from_db(sha_256_val)

    if img_flag_id == 0:
        save_flag = image_lib.save_image_file(data_image, final_path)
        if save_flag is True:
            print('Saving image file as ' + final_path + '...success')

    if img_flag_id == 0:
        record_id = add_apod_to_db(apod_data['title'], apod_data['explanation'], final_path, sha_256_val)
        if record_id > 0:
            print('Adding APOD to image cache DB...success')
    else:
        print('APOD image is already in cache')

    if img_flag_id != 0:
        record_id = img_flag_id

    return record_id


def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """

    con = sqlite3.connect(image_cache_db)

    cur = con.cursor()

    cur.execute('select max(id) from  APOD')

    fetch_id = cur.fetchone()

    id_create = 0

    if fetch_id is None:
        id_create = 1
    else:
        id_create = int((0 if fetch_id[0] is None else fetch_id[0])) + 1

    # Inserting data into DB
    insert_apod = """ INSERT INTO APOD ( id, APOD_TITLE , APOD_EXPAIN , file_path , SHA256_VAL ) VALUES (?,?, ?, ?, ?); """

    image_apod_data = (id_create,
                       title,
                       explanation,
                       file_path,
                       sha256)

    # Executing query to add new people data to table
    cur.execute(insert_apod, image_apod_data)

    # Commit the changes
    con.commit()

    cur.execute('select max(id) from  APOD')

    # Checking if data is inserted successfully
    newmaxid = cur.fetchone()

    con.close()

    if id_create is newmaxid[0]:
        return id_create
    else:
        return 0


def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """

    con = sqlite3.connect(image_cache_db)

    cur = con.cursor()

    str_image = str(image_sha256)

    # Query to fetch id from APOD using SHA256 value
    image_fetch = ("""SELECT id FROM APOD WHERE SHA256_VAL = '%s'""" % (str_image))

    cur.execute(image_fetch)

    data = cur.fetchone()

    if data is None:
        print('APOD image is not already in cache')
        return 0
    else:
        return int((0 if data[0] is None else data[0]))


def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body

    dat = os.path.splitext(image_url)

    ext = dat[-1]

    new_title = image_title.strip().replace(' ', '_')
    new_title_1 = re.sub('[\W]+', '', new_title)

    file_path = os.path.join(image_cache_dir, new_title_1)

    # concatenating Final path extension
    final_path = file_path + ext

    return final_path


def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary

    con = sqlite3.connect(image_cache_db)

    cur = con.cursor()

    # Gathering info from DB
    if image_id > 0:
        cur.execute('select APOD_TITLE, APOD_EXPAIN , file_path  from  APOD where id =' + str(image_id) + ' ')

    data = cur.fetchone()

    apod_info = {
        'title': data[0],
        'explanation': data[1],
        'file_path': data[2],
    }
    return apod_info


def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI

    con = sqlite3.connect(image_cache_db)

    cur = con.cursor()

    cur.execute('select APOD_TITLE  from  APOD ')

    data = cur.fetchall()

    return data


if __name__ == '__main__':
    main()

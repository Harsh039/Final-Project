'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''

from datetime import datetime
import os
import requests


def main():
    # TODO: Add code to test the functions in this module
    # get_apod_info('2022-12-12')
    return


def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """

    response = None
    # My Nasa Key
    k1 = "nsPC6odNRqQYfYEZjdpWT5eWPXsfqR5eyt2Cf4Pf"

    API_url = "https://api.nasa.gov/planetary/apod"
    args = {
        'api_key': k1,
        'date': apod_date,
        'hd': 'True'
    }
    # Making the API Call
    response = requests.get(API_url, params=args)
    if response.status_code == 200:
        response_data = response.json()
        print('Getting ' + str(apod_date) + ' APOD information from NASA...success')

    return response_data


def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """

    if apod_info_dict['media_type'] == 'image':
        url_hd = apod_info_dict['hdurl']
    else:
        # In case the video is from youtube
        if apod_info_dict['url'].find("youtube") != -1:
            url_cont = apod_info_dict['url'].split('?')
            url_cont_2 = url_cont[0].split('/')
            video_id = url_cont_2[-1]
            url_hd = 'https://img.youtube.com/vi/' + video_id + '/hqdefault.jpg'
        # In case the video is from vimeo
        elif apod_info_dict['url'].find("vimeo") != -1:
            url_cont = apod_info_dict['url'].split('?')
            url_cont_2 = url_cont[0].split('/')
            video_id = url_cont_2[-1]
            url_hd = 'https://vumbnail.com/' + video_id + '.jpg'
        else:
            url_hd = apod_info_dict['url']

    return url_hd


if __name__ == '__main__':
    main()

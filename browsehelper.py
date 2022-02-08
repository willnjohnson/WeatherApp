'''
    browsehelper.py
    TMWRK

    Open browser for webpage (generic browsing, Wiki browsing)

    References: mediawiki.org/wiki/API:Opensearch
'''

import os
import webbrowser
import requests
from PIL import Image, ImageEnhance

# gets the absolute path to where main.py is
main_path = os.path.dirname(os.path.abspath(__file__))
class Wiki():
    def search(city):
        S = requests.Session()

        URL = "https://en.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "opensearch",
            "namespace": "0",
            "search": city,
            "limit": "1",
            "format": "json",
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        URL = DATA[3][0]

        # visit an existing wiki article of city
        # Note: London, GB doesn't actually find the city London, just an article related to it
        webbrowser.open(URL)
    
    def getImage(lat, lon):
        if lat == None or lon == None:
            return None

        image_path = None

        S = requests.Session()

        URL = "https://en.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "query",
            "prop": "pageimages",
            "inprop": "url",
            "piprop": "original",
            "generator": "geosearch",
            "ggsradius": 10000,
            "ggslimit": 10,
            "ggscoord": str(lat) + "|" + str(lon),
            "limit": 10,
            "format": "json",
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        PAGES = DATA['query']['pages']

        for v, k in PAGES.items():
            # iterate through each media page
            imgurl = k['original']['source']

            # find either first .png or .jpg (we don't care about .svg)
            if imgurl.endswith('.png') or imgurl.endswith('.jpg'):
                suffix = '.png' if imgurl.endswith('.png') else '.jpg'

                # retrieve image
                res = requests.get(imgurl, stream=True)
                if res.status_code == 200:
                    # save image locally
                    image_path = main_path + '/cc' + suffix
                    with open (image_path, 'wb') as fout:
                        fout.write(res.content)
                    
                    # darken image (Reference: https://pythonexamples.org/python-pillow-adjust-image-brightness/)
                    im = Image.open(image_path) # open image
                    im_out = ImageEnhance.Brightness(im).enhance(0.4) # darken
                    im_out.save(image_path) # write darkened file

                    # return file path to image
                return image_path
        return None

class Generic():
    def searchURL(url):
        webbrowser.open(url)
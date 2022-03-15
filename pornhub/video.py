from .core import *
import json
import re

class Video(object):

    def __init__(self, ProxyDictionary, *args):
        self.ProxyDictionary = ProxyDictionary

    def _loadPage(self, url, viewkey):

        if url and isVideo(url):
            r = requests.get(url, headers=HEADERS, proxies=self.ProxyDictionary)
        else:
            r = requests.get(BASE_URL + VIDEO_URL + viewkey, headers=HEADERS, proxies=self.ProxyDictionary)
        
        html = r.text
        # print(r.url)
        return BeautifulSoup(html, "lxml")
    
    # Scrap duration, upload_date, author, img_url, embed_url, accurate_views
    def _scrapScriptInfo(self, soup_data):

        data = dict()
        script_dict = json.loads(soup_data.replace("'",'"'))

        data["author"] = script_dict["author"] 
        data["embed_url"] = script_dict['embedUrl']
        data["img_url"] = script_dict["thumbnailUrl"]
        data["duration"] = ":".join(re.findall(r'\d\d',script_dict['duration']))
        data["upload_date"] = re.findall(r'\d{4}-\d{2}-\d{2}',script_dict['uploadDate'])[0]
        data["accurate_views"] = int(script_dict['interactionStatistic'][0]['userInteractionCount'].replace(',',''))

        return data

    def _scrapInfo(self, soup_data):

        data = {
            "title"             : None,     # string
            "views"             : None,     # string
            "accurate_views"    : None,     # integer
            "rating"            : None,     # integer
            "duration"          : None,     # string
            "loaded"            : None,     # string
            "upload_date"       : None,     # string
            "likes"              : None,     # string
            "accurate_likes"     : None,     # integer
            "dislikes"           : None,     # string
            "accurate_dislikes"  : None,     # integer
            "favorite"          : None,     # string
            "author"            : None,     # string
            "pornstars"         : None,     # list
            "categories"        : None,     # list
            "tags"              : None,     # list
            "productions"       : None,     # list
            "img_url"           : None,     # string
            "embed_url"         : None      # string
        }

        # Scrap duration, upload_date, author, img_url, embed_url, accurate_views
        try:
            script_data = self._scrapScriptInfo(soup_data.find("script", type='application/ld+json').text)
        except:
            data['title'] = '***Video not available in your country***'
            return data

        for key in script_data:
            data[key] = script_data[key]
        

        video = soup_data.find("div", class_='video-wrapper')
        data['title'] = video.find("span", class_='inlineFree').text
        data['views'] = video.find("span", class_="count").text  # Scrap view
        data['rating'] = int(video.find("span", class_="percent").text.replace('%',''))  # Scrap rating
        data["loaded"] = video.find("div", class_="videoInfo").text  # Scrap loaded
        data["likes"] = video.find("span", class_="votesUp").text  # Scrap like
        data["accurate_likes"] = video.find("span", class_="votesUp")["data-rating"]  # Scrap accurate_like
        data["dislikes"] = video.find("span", class_="votesDown").text  # Scrap dislike
        data["accurate_dislikes"] = video.find("span", class_="votesDown")["data-rating"] # Scrap accurate_dislike
        data["favorite"] = video.find("span", class_="favoritesCounter").text.strip() # Scrap favorite

        # Scrap pornstars
        pornstars = [] 
        for star in video.find_all('a', class_='pstar-list-btn'):
            pornstars.append(star.text.strip())
        data["pornstars"] = pornstars
        
        # Scrap categories
        categories = []
        for category in video.find("div", class_="categoriesWrapper").find_all('a', class_="item"):
            categories.append(category.text)
        data["categories"] = categories

        # Scrap tags
        tags = []
        for tag in video.find("div", class_="tagsWrapper").find_all('a', class_="item"):
            tags.append(tag.text)
        data["tags"] = tags

        # Scrap productions
        productions = []
        for prod in video.find("div", class_="productionWrapper").find_all('a', class_="item"):
            productions.append(prod.text)
        data["productions"] = productions

        return data

    def getVideo(self, url=None, viewkey=None, *args):
        """
        Get video informations.
        You can enter the full video url or just the viewkey
        :url: video url on phub
        :viewkey: viewkey of video
        """
        if url or viewkey:
            data = self._scrapInfo(self._loadPage(url, viewkey))
        else:
            return print('URL or Viewkey not entered')
        return data


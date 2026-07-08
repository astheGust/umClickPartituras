from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("SERP_API_KEY")

allowed = [
  "musescore",
  "youtube",
  "musicnotes",
  "sheetmusicdirect",
  "sheetmusicplus",
  "scribd",
  "lasolsheet",
  "tomplay",
  "mymusicsheet"
]



def searchQuery(query,instrumentList):
    sheets = {}
    try:
        if (instrumentList[0] != ""):
            for instrument in instrumentList:
                search = GoogleSearch({
                "engine":"google_images",
                "q": f"{query} {instrument} sheet",
                "safe":"active",
                "location": "Brazil",
                "hl": "pt",
                "gl": "br",
                "google_domain": "google.com.br",
                "api_key":API_KEY
                })
                results  = search.get_dict()
                rawDices =  dict(results)
                imageResult = rawDices.get("images_results",[])
                for result in imageResult:
                    source = result.get("source","").lower()
                    link = result.get("link","")
                    image = result.get("original","")
                    for site in allowed:
                        if site.lower() in source:
                            if site not in sheets:
                                sheets[site] = []
                                duplicate = False
                            for item in sheets[site]:
                                if(item["url"] == link):
                                    duplicate = True
                                    break
                            if(not duplicate):
                                sheets[site].append({
                                "url":link,
                                "img":image,
                                "instrument":instrument})
        else:
            search = GoogleSearch({
                "engine":"google_images",
                "q": f"{query} sheet",
                "safe":"active",
                "location": "Brazil",
                "hl": "pt",
                "gl": "br",
                "google_domain": "google.com.br",
                "api_key":API_KEY
                })
            results  = search.get_dict()
            rawDices =  dict(results)
            imageResult = rawDices.get("images_results",[])
            for result in imageResult:
                source = result.get("source","").lower()
                link = result.get("link","")
                image = result.get("original","")
                for site in allowed:
                    if site.lower() in source:
                        if site not in sheets:
                            sheets[site] = []
                        sheets[site].append({
                            "url":link,
                            "img":image})
    except Exception as err:
        raise Exception("Erro na conexão com a API de busca:",err)
    return sheets
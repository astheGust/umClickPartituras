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


from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SERP_API_KEY")

def duplicado(link_atual, lista_do_site):
    for item in lista_do_site:
        if item["url"] == link_atual:
            return True 
    return False


def searchQuery(query, instrumentList):
    sheets = {}
    try:
        if instrumentList and instrumentList[0] != "":
            for instrument in instrumentList:
                search = GoogleSearch({
                    "engine": "google_images",
                    "q": f"{query} {instrument} sheet",
                    "safe": "active",
                    "location": "Brazil",
                    "hl": "pt",
                    "gl": "br",
                    "google_domain": "google.com.br",
                    "api_key": API_KEY,
                    "num": "30"
                })
                imageResult = search.get_dict().get("images_results", [])[:50]
                for result in imageResult:                    
                    #link = result.get("link", "").lower()
                    source = result.get("source", "").lower()
                    image = result.get("thumbnail", "")
                    
                    for site in allowed:
                        if site in source:
                            if site not in sheets:
                                sheets[site] = []
                            
                            if not duplicado(result.get("link"), sheets[site]):
                                sheets[site].append({
                                    "url": result.get("link"),
                                    "img": image
                                })
        else:
            search = GoogleSearch({
                "engine": "google_images",
                "q": f"{query} sheet",
                "safe": "active",
                "location": "Brazil",
                "hl": "pt",
                "gl": "br",
                "google_domain": "google.com.br",
                "api_key": API_KEY,
            })
            imageResult = search.get_dict().get("images_results", [])[:50]
            for result in imageResult:
                #link = result.get("link", "").lower()
                source = result.get("source", "").lower()
                image = result.get("thumbnail", "")
                
                for site in allowed:
                        if site in source:
                            if site not in sheets:
                                sheets[site] = []
                            
                            if not duplicado(result.get("link"), sheets[site]):
                                sheets[site].append({
                                    "url": result.get("link"),
                                    "img": image
                                })
                            
    except Exception as err:
        raise Exception("Erro na conexão com a API de busca:", err)
        
    return sheets
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

traducao_instrumentos = {
    "piano": "piano",
    "violino": "violin",
    "flauta": "flute",
    "violão": "guitar",
    "bateria": "drums",
    "violoncelo": "cello",
    "saxofone": "saxophone"
}

def searchQuery(query, instrumentList):
    sheets = {}
    try:
        instrumentos_ingles = [traducao_instrumentos.get(i.lower(), i) for i in instrumentList]
        sites_operator = " OR ".join([f"site:{site}" for site in allowed])
        instruments_str = ""
        if instrumentos_ingles and instrumentos_ingles[0] != "":
            instruments_str = f"({' OR '.join(instrumentos_ingles)})"
        final_query = f"{query} {instruments_str} music sheet ({sites_operator})".strip()

        search = GoogleSearch({
            "engine": "google_images",
            "q": final_query,
            "safe": "active",
            "location": "Brazil",
            "hl": "pt",
            "gl": "br",
            "google_domain": "google.com.br",
            "api_key": API_KEY
        })
        
        results = search.get_dict()
        image_results = results.get("images_results", [])
        
        for result in image_results:
            source = result.get("source", "").lower()
            link = result.get("link", "")
            image = result.get("thumbnail", "")
            
            for site in allowed:
                if site.lower() in source:
                    if site not in sheets:
                        sheets[site] = []
                    
                    if not any(item["url"] == link for item in sheets[site]):
                        sheets[site].append({
                            "url": link,
                            "img": image
                        })
                    break 
    except Exception as err:
        raise Exception(f"Erro na conexão com a API de busca: {str(err)}")
        
    return sheets
from serpapi import GoogleSearch
import os
from flask import Flask,jsonify,request
from flask_cors import CORS
from dotenv import load_dotenv
app = Flask(__name__)
CORS(app)
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

ins=["piano","violin"]


def searchQuery(query,instrumentList):
    sheets = {}

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
                    
    return sheets


@app.route("/images",methods=["GET"])
def imgsLinks():
    query = request.args.get("q","")
    filter = request.args.get("filter","")
    instruments = filter.split(",")
    print(instruments)
    if not query: return jsonify({"err":"Pesquisa Vazia"}),400
    try:
        sheets = searchQuery(query,instruments)
    except Exception as error:
        print(error)
        return jsonify({
            "sucess":False,
            "error": str(error),
            'statusCode':500
        }), 500

    count = 0

    for item in sheets.items():
        if len(item[1]) > 2:
            count+=1

    if count > 2:
        return jsonify({
            "sucess":True,
            "message":"Dados Enviados",
            "statusCode":200,
            "data":sheets
            }),200
    else: return jsonify({
            "sucess":False,
            "message":"Itens insuficientes",
            'statusCode':206
        }), 206

if __name__ == "__main__":
    print("server rodando!")
    app.run(debug=True)
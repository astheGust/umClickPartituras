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


@app.route("/images",methods=["GET"])
def imgsLinks():
    query = request.args.get("q","")
    if not query: return jsonify({"err":"Pesquisa Vazia"}),400
    try:       
        search = GoogleSearch({
        "engine":"google_images",
        "q": query,
        "safe":"active",
        "location": "Brazil",
        "hl": "pt",
        "gl": "br",
        "google_domain": "google.com.br",
        "api_key":API_KEY
        })

        results  = search.get_dict()

        if "error" in results:
            return jsonify({"error":results["error"]}),400

        rawDices =  dict(results)
        imageResult = rawDices.get("images_results",[])
        sheets={}
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

    except Exception as error:
        print(error)
        return jsonify({
            "error": str(error)
        }), 500

    return jsonify(sheets)

if __name__ == "__main__":
    print("server rodando!")
    app.run(debug=True)
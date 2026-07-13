from flask import Flask, render_template, send_from_directory,jsonify,request,g
from flask_cors import CORS
from hashPass import hashPassword,comparePassword
from bdConnection import sqlSelect,sqlQuery
from sendEmail import enviarEmail
from backApi import searchQuery
import os
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from functools import wraps
load_dotenv()
rota = os.getenv("ROTAATUAL")
JWT_SECRET = os.getenv("JWTSECRET")
app = Flask(__name__)
CORS(app)

@app.route("/styles.css")
def styles():
    return send_from_directory(os.path.join(app.root_path, ".."), "styles.css")

@app.route("/logic.js")
def logic():
    return send_from_directory(os.path.join(app.root_path, ".."), "logic.js")

@app.route("/src/imgs/<filename>")
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, "imgs"), filename)

@app.route("/")
def home():
    return render_template("index.html")

def authenticateToken(func):
    @wraps(func)
    def verificar():
        authHeader = request.headers.get("Authorization")
        token = authHeader.split(" ")[1]
        if (not token): return jsonify({"message":"Token não encontrado"}),403
        try:
            decoded = jwt.decode(token,JWT_SECRET,algorithms="HS256")
            g.user = decoded
        except Exception as err:
            raise Exception("Token Inválido",err)

        return func()
    return verificar


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register",methods=["POST"])
def registerAccount():
    userEmail,userPass = request.json.values()
    results = sqlSelect("SELECT user_id,verificado FROM usuarios WHERE email = %s",[userEmail])
    if(len(results) == 0):
        try:
            hashedPassword = hashPassword(userPass)
            sqlQuery("INSERT INTO usuarios(email,hashPass,verificado) VALUES(%s,%s,%s)",[userEmail,hashedPassword,0])
            token = jwt.encode({
                "email":userEmail,
                "exp":datetime.now(timezone.utc) + timedelta(minutes=10)
                    },JWT_SECRET,algorithm="HS256")
            link = f"{rota}/verify-email?token={token}"
            enviarEmail(userEmail,link)
            return jsonify({"message":"Usuário cadastrado com sucesso! Verifique seu Email!"}),200
        except Exception as err:
            return jsonify({ #erro nas funções enviarEmail e sql
            "success": False,
            "message": str(err)
        }), 500
    else:
        user_id,verificado = results[0]
        try:
            if(verificado == 0):
                tokenNovo = jwt.encode({
                    "email":userEmail,
                    "exp":datetime.now(timezone.utc) + timedelta(minutes=10)
                        },JWT_SECRET,algorithm="HS256")
                link = f"{rota}/verify-email?token={tokenNovo}"
                enviarEmail(userEmail,link)
                return jsonify({"message":"Novo E-mail de verificação enviado!"}),200 
            else:
                return jsonify({"message":"Usuário já cadastrado no sistema"}),400 
        except Exception as err:
            return jsonify({ #erro nas funções enviarEmail e sql
            "success": False,
            "message": str(err)
        }), 500


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def loginAccount():
    userEmail,userPass = request.json.values()
    results = sqlSelect("SELECT user_id,hashPass,verificado FROM usuarios WHERE email = %s",[userEmail])
    if(len(results) == 0): return jsonify({"message":"Usuario não encontrado"}),404
    user_id,hashPass,verificado = results[0]

    if(verificado == 0): return jsonify({"verificado":False,"message":"Usuário não verificado!"})
    passCompare = comparePassword(userPass, hashPass)
    if(not passCompare):return jsonify({"message":"senha incorreta!"}),404
    token = jwt.encode({
            "userId":user_id,
            "exp":datetime.now(timezone.utc) + timedelta(days=7)
            },JWT_SECRET,algorithm="HS256")
    return jsonify({"message":"Token de Autenticação enviado!","success":True,"token":token}),200

@app.route("/verify-email")
def verifyEmail():
    token = request.args.get("token")
    if(not token): return jsonify({"message":"Token inválido ou expirado!"}),400
    try:
        decoded = jwt.decode(token,JWT_SECRET,algorithms=["HS256"])
        email = decoded.get("email")
        sqlQuery("UPDATE usuarios SET verificado = 1 WHERE email  = %s",[email])
        return render_template("login.html")
    except Exception as err:
        return jsonify({ #erro da função sql
            "success": False,
            "message": str(err)
        }), 500

@app.route("/sendEmail",methods=["POST"])
def confirmEmail():
    data = request.json
    email = data["email"]
    results = sqlSelect("SELECT user_id FROM usuarios WHERE email = %s",[email])
    if(len(results) > 0):
        try:
            tokenNovo = jwt.encode({
                        "email":email,
                        "exp":datetime.now(timezone.utc) + timedelta(minutes=10)
                            },JWT_SECRET,algorithm="HS256")
            link = f"{rota}/verify-email?token={tokenNovo}"
            enviarEmail(email,link)
            return jsonify({"message":"Novo E-mail de verificação enviado!"}),200
        except Exception as err:
            return jsonify({ #erro nas funções enviarEmail e sql
            "success": False,
            "message": str(err)
        }), 500

@app.route("/images",methods=["GET"])
def imgsLinks():

    query = request.args.get("q","")
    filter = request.args.get("filter","")
    instruments = filter.split(",")
    if not query: return jsonify({"err":"Pesquisa Vazia"}),400
    try:
        sheets = searchQuery(query,instruments)
    except Exception as err:
        return jsonify({ #erro na conexão com a API de busca
            "success":False,
            "message": str(err),
            'statusCode':500
        }), 500


    imgsCount = sum(len(img) for img in sheets.values())
    if imgsCount > 1:
        return jsonify({
            "success": True, 
            "message": "Dados Enviados",
            "statusCode": 200,
            "data": sheets
        }), 200
    else: 
        return jsonify({
            "success": False, 
            "message": "Itens Insuficientes",
            "data": {"pesquisa": query, "filtros": filter},
            "statusCode": 404,
            "dado": sheets
        }), 404
#
#Rotas Protegidas:

#EM DESENVOLVIMENTO

#@app.route("/favorites",methods=["GET"])
#def favoritesRoute():
#    return render_template("favorites.html")

@app.route("/favorites",methods=["POST"])
@authenticateToken
def postFavorites():
    data = request.json
    url = data.get("url")
    imgHref = data.get("href")
    results = sqlSelect("SELECT sheet_id,image_url FROM partituras WHERE url = %s",[url])
    user = g.user["userId"]
    if(len(results) == 0):
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
        try:
            source = next((item for item in allowed if item in url),None)
            if(source and imgHref):
                sqlQuery("INSERT INTO partituras(site,url,image_url) VALUES(%s,%s,%s)",[source,url,imgHref])
            else:
                sqlQuery("INSERT INTO partituras(url) VALUES(%s)",[url])

            sheet_id = sqlSelect("SELECT sheet_id FROM partituras WHERE url = %s",[url])[0][0]

            sqlQuery("INSERT INTO usuarios_favoritos(user_id,sheet_id) VALUES(%s,%s)",[user,sheet_id])
            
        except Exception as err:
            return jsonify({ #erro nas funções sql
            "success": False,
            "message": str(err)
        }), 500
    else:
        try:
            sheet_id = sqlSelect("SELECT sheet_id FROM partituras WHERE url = %s",[url])[0][0]
            sqlQuery("INSERT INTO usuarios_favoritos(user_id,sheet_id) VALUES(%s,%s)",[user,sheet_id])
        except Exception as err:
            return jsonify({ #erro nas funções sql
            "success": False,
            "message": str(err)
        }), 500
    return jsonify({
            "message":"Dados Enviados",
            "statusCode":200,
            "musica":url
            }),200

@app.route("/favorites",methods=["DELETE"])
@authenticateToken
def removeFavorite():
    data = request.json
    unfavoriteUrl = data["url"]
    id_user = g.user["userId"]
    if(unfavoriteUrl):
        try:
            results = sqlSelect("SElECT sheet_id FROM partituras WHERE url = %s",[unfavoriteUrl])
            sheet_id = results[0][0]

            sqlQuery("DELETE FROM usuarios_favoritos WHERE user_id = %s AND sheet_id = %s",[id_user,sheet_id])

            return jsonify({"message":"Url retirada dos favoritos do Usuário"})
        except Exception as err:
            return jsonify({ #erro nas funções sql
            "success":False,
            "message": str(err),
            'statusCode':500
        }), 500

#EM DESENVOLVIMENTO

@app.route("/checkFavorites",methods=["GET"])
@authenticateToken
def checkFavorites():
    id_user = g.user["userId"]
    if(id_user):
        try:
            rows = sqlSelect("SELECT partituras.url,partituras.image_url FROM usuarios_favoritos JOIN partituras ON usuarios_favoritos.sheet_id = partituras.sheet_id WHERE usuarios_favoritos.user_id = %s",[id_user])
            if(len(rows) !=0):
                return jsonify({"favoritos":rows}),200
            else:
                return jsonify({"message":"NADA AQUI"})
        except Exception as err:
            return jsonify({
            "success":False,
            "message": str(err),
            'statusCode':500
        }), 500
    else:
        return jsonify({"message":"error"}),404
        
@app.route("/health",methods=["GET"])
def heathCheck():
    try:
        sqlSelect("SELECT user_id FROM usuarios WHERE user_id = %s",["2"])
        return jsonify({
                "success": True,
                "message": "API e Banco de Dados estão ONLINE!"
            }), 200
        
    except Exception as err:
        return jsonify({
            "success": False,
            "message": "API online, mas o Banco de Dados falhou!",
            "error": str(err)
        }), 500
        
if __name__ == '__main__':
    app.run(debug=True)

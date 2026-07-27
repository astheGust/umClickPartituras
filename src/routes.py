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
        if(authHeader):           
            token = authHeader.split(" ")[1]
            if (not token): return jsonify({"message":"Token não encontrado"}),404
            elif(token):
                try:
                    decoded = jwt.decode(token,JWT_SECRET,algorithms="HS256")
                    g.user = decoded
                    
                except jwt.ExpiredSignatureError:
                    return jsonify({"message":"Token expirado!"}),401
                except Exception as err:
                    raise Exception("Erro ao validar o token",err)
                return func()
        else:
            return jsonify({"message":"AuthHeader vazio"}),403
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
            mensagem = enviarEmail(userEmail,link)
            if(mensagem == True):
                return jsonify({"message":"Usuário cadastrado com sucesso! Verifique seu Email!"}),200
            elif isinstance(mensagem,dict):
                return jsonify({"message":"Erro ao tentar enviar o E-mail", "err":mensagem.err})
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
    if(not passCompare):return jsonify({"message":"senha incorreta!"}),401
    acessToken = jwt.encode({
            "userId":user_id,
            "exp":datetime.now(timezone.utc) + timedelta(days=7)
            },JWT_SECRET,algorithm="HS256");
    refreshToken = jwt.encode({
            "userId":user_id,
            "exp":datetime.now(timezone.utc) + timedelta(days=30)
            },JWT_SECRET,algorithm="HS256");
    return jsonify({"message":"Token de Autenticação enviado!","success":True,"acessToken":acessToken,"refreshToken":refreshToken}),200

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
    else:
        return jsonify({"message":"Erro referente a verificação do email!"}),404


@app.route("/images",methods=["GET"])
def imgsLinks():
    query = request.args.get("q","")
    filter = request.args.get("filter","")
    instruments = filter.split(",")
    if not query or query == "": return jsonify({"err":"Pesquisa Vazia"}),400
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

#Rotas Protegidas:

@app.route("/favoritesPage")
def favorites():
    return render_template("favorites.html")

@app.route("/favorites",methods=["POST"])
@authenticateToken
def postFavorites():
    data = request.json
    url = data.get("url")
    imgHref = data.get("href")
    annotation = data.get("annotation")
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
            sqlQuery("INSERT INTO usuarios_favoritos(user_id,sheet_id,anotacoes) VALUES(%s,%s,%s)",[user,sheet_id,annotation])
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
            print(err)
            return jsonify({ #erro nas funções sql
            "success":False,
            "message": str(err),
            'statusCode':500
        }), 500

@app.route("/checkFavorites",methods=["GET"])
@authenticateToken
def checkFavorites():
    #data = request.json
    id_user = g.user["userId"]
    #query = data["query"]
    if(id_user):
        try:
            rows = sqlSelect("SELECT partituras.url,partituras.image_url,usuarios_favoritos.anotacoes FROM usuarios_favoritos JOIN partituras ON usuarios_favoritos.sheet_id = partituras.sheet_id WHERE usuarios_favoritos.user_id = %s",[id_user])
            if(len(rows) !=0):
                return jsonify({"favoritos":rows}),200
            else:
                return jsonify({"favoritos":[],"message":"Nada encontrado"}),200
        except Exception as err:
            print(err)
            return jsonify({
            "success":False,
            "message": str(err),
            'statusCode':500
        }), 500
    else:
        return jsonify({"message":"error"}),404
        
@app.route("/token",methods=["POST"])
def refreshAcesstoken():
    data = request.json
    refToken = data["token"]
    if(refToken != ""):
        try:
            decoded = jwt.decode(refToken,JWT_SECRET,algorithms=["HS256"])
            user = decoded.get("userId")
            acessToken = jwt.encode({
                    "userId":user,
                    "exp":datetime.now(timezone.utc) + timedelta(days=7)
                    },JWT_SECRET,algorithm="HS256");
            refreshToken = jwt.encode({
                    "userId":user,
                    "exp":datetime.now(timezone.utc) + timedelta(days=30)
                    },JWT_SECRET,algorithm="HS256");
            return jsonify({"message":"Novo token fornecido!","success":True,"acessToken":acessToken,"refreshToken":refreshToken}),200
        except jwt.ExpiredSignatureError:
            return jsonify({"message":"Token expirado!"}),401
        except Exception as err:
            raise Exception({"Erro ao validar o token",err})
        
#@app.route("/checkPassword",methods=["POST"])
#@authenticateToken
#def checkUserpassword():
#    id_user = g.user["userId"]
#    data = request.json
#    payloadPass = data["password"]
#    try:
#        currentPass = sqlSelect("SELECT hashPassword FROM usuarios WHERE user_id = %s",[id_user])[0[0]]
#        if(not payloadPass or not currentPass): return jsonify({"message":"erro em resgastar um dos valores"}),400
#        if(comparePassword(payloadPass,currentPass)):
#            return jsonify({"message":"Senha corresponde","success":True}),200
#        else:
#            return jsonify({"message":"Senha não corresponde","success":False}),401
#    except Exception as err:
#                print(err)
#                return jsonify({ #erro nas funções sql
#                "success":False,
#                "message": str(err),
#                'statusCode':500
#            }), 500
#    
@app.route("/changePassword",methods=["PATCH"])
@authenticateToken
def changeUserpassword():
    id_user = g.user["userId"]
    data = request.json
    currentPass = data["current"]
    newPass = data["newPassword"]
    try:
        if( not currentPass != "" or not newPass != ""):
            return jsonify({"message":"Não foi possível processar a mudança de senha"}),400
        currentHashpass = sqlSelect("SELECT hashPass FROM usuarios WHERE user_id = %s",[id_user])[0][0]
        if(not currentHashpass): return jsonify({"message":"erro em resgastar um valor"}),400
        if(comparePassword(currentPass,currentHashpass)):
            hashedPass = hashPassword(newPass)
            sqlQuery("UPDATE usuarios SET hashPass = %s WHERE user_id = %s",[hashedPass,id_user])
            return jsonify({"message":"Senha alterada com sucesso!","success":True}),200
        else:
            return jsonify({"message":"Senha não corresponde","success":False}),401
    except Exception as err:
            print(err)
            return jsonify({ #erro nas funções sql
            "success":False,
            "message": str(err),
            'statusCode':500
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
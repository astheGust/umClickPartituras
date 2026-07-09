import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAILPASS = os.getenv("EMAILSECRET")


def enviarEmail(destinatario,link):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587 #porta padrão para tls/starttls
    remetente = EMAIL
    senha = EMAILPASS

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Verifique sua conta"    

    html_body = f"<p>Clique no link para realizar a verificação: <a href={link}>Verificar</a></p>"
    msg.attach(MIMEText(html_body,"html","utf-8"))

    server = None
    try:
        print("tentando conectar")
        server = smtplib.SMTP(smtp_server,smtp_port)
        server.starttls()
        server.login(remetente,senha)

        server.sendmail(remetente,destinatario,msg.as_string())
    except Exception as err:
        print("error")
        raise Exception("Erro ao enviar E-mail:",err)
    finally:
        if(server is not None):
            server.quit()

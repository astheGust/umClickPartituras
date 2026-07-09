import os

from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()

EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("BREVO_API_KEY")


def enviarEmail(destinatario, link):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender={
            "name": "Click Partituras",
            "email": EMAIL
        },
        to=[
            {
                "email": destinatario
            }
        ],
        subject="Verifique sua conta",
        html_content=f"""
<html>
<body>

<h2>Bem-vindo ao Click Partituras!</h2>

<p>
Clique no botão abaixo para verificar sua conta.
</p>

<p>
<a href="{link}"
style="
background:#2563eb;
color:white;
padding:12px 20px;
text-decoration:none;
border-radius:6px;
display:inline-block;
">
Verificar Conta
</a>
</p>

<p>
Caso o botão não funcione, copie este link:
</p>

<p>{link}</p>

</body>
</html>
"""
    )

    try:
        api_instance.send_transac_email(email)
        return True

    except ApiException as err:
        print(err)
        raise
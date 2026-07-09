import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def enviarEmail(destinatario, link):
    try:
        resposta = resend.Emails.send(
            {
                "from": "onboarding@resend.dev",
                "to": [destinatario],
                "subject": "Verifique sua conta",
                "html": f"""
                <html>
                    <body>
                        <h2>Bem-vindo ao Click Partituras!</h2>

                        <p>
                            Clique no botão abaixo para verificar sua conta:
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
                            Caso o botão não funcione, copie e cole o link abaixo no navegador:
                        </p>

                        <p>{link}</p>
                    </body>
                </html>
                """
            }
        )

        print("Email enviado com sucesso!")
        print(resposta)

        return True

    except Exception as err:
        print("Erro ao enviar email:")
        print(err)
        raise
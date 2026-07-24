let url = ""
if (window.location.href.includes("https")) {
    url = "https://umclickpartituras.onrender.com"
} else {
    url = "http://127.0.0.1:5000"
}

window.addEventListener("DOMContentLoaded", () => {

    const mode = localStorage.getItem("mode")
    const token = localStorage.getItem("acessToken")
    const isFavoritesPage = window.location.href.includes("/favorites")
    const signSection = document.getElementById("signSection")
    const diamondBtn = document.getElementById("diamondBtn")
    const navDropdown = document.getElementById("navDropdown")
    const navFavorites = document.getElementById("navFavorites")
    const navHome = document.getElementById("navHome")
    const navLogout = document.getElementById("navLogout")

    if (mode) {
        document.getElementById("lightMode").innerText = "Dark"
        document.documentElement.classList.add("dark")
    } else {
        document.documentElement.classList.remove("dark")
    }
    if (token) {
        if (signSection) signSection.classList.add("hidden")
        if (diamondBtn) diamondBtn.classList.remove("hidden")
        if (navLogout) navLogout.classList.remove("hidden")

        if (isFavoritesPage && navHome) {
            navHome.classList.remove("hidden")
        }
        if (!isFavoritesPage && navFavorites) {
            navFavorites.classList.remove("hidden")
        }
    } else {
        if (signSection) signSection.classList.remove("hidden")
        if (diamondBtn) diamondBtn.classList.add("hidden")
        if (navDropdown) navDropdown.classList.add("hidden")
        if (navLogout) navLogout.classList.add("hidden")
        if (navFavorites) navFavorites.classList.add("hidden")
        if (navHome) navHome.classList.add("hidden")
    }
})

let active = !!localStorage.getItem("mode")
document.getElementById("lightMode").addEventListener("click", () => {
    active = !active
    document.documentElement.classList.toggle("dark")
    if (active) {
        document.getElementById("lightMode").innerText = "Light"
        localStorage.setItem("mode", active)
    }
    else {
        document.getElementById("lightMode").innerText = "Dark"
        localStorage.removeItem("mode")

    }

})

const loading = document.getElementById("loading")
const dice = document.getElementById("query")
const contentBlock = document.getElementById("content")
const instrumentsCheckbox = document.querySelectorAll(".instrumentCheckbox")
const filterP = document.getElementById("filterText")
const instruments = []

function clean(target) {
    switch (target) {
        case "content":
            contentBlock.innerHTML = ""
            break
        case "afterSearch":
            dice.value = ""
            loading.style.display = "none"
            filterP.innerText = ""
            instrumentsCheckbox.forEach((checkBox) => {
                checkBox.checked = false
            })
            instruments.splice(0, instruments.length)
            break
    }
}

function showPopUp(message) {
    const popUp = document.createElement("div")
    popUp.classList.add("popUpContainer")
    popUp.textContent = message
    document.body.appendChild(popUp)

    setTimeout(() => {
        popUp.remove()
    }, 3000)
}

//pedir um novo token

async function fetchComAuth(url, options = {}) {
    let token = localStorage.getItem("acessToken");
    options.headers = {
        ...options.headers,
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };

    let response = await fetch(url, options);

    if (response.status === 401) {
        const renovou = await newToken();

        if (renovou) {
            token = localStorage.getItem("acessToken");
            options.headers["Authorization"] = `Bearer ${token}`;
            response = await fetch(url, options);
        }
    }

    return response;
}

const newToken = async () => {
    let token = localStorage.getItem("refreshToken")
    if (token) {
        try {
            let req = await fetch(`${url}/token`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token })
            })
            if (req.status === 401) {
                alert("Sua sessão expirou. Por favor, faça login novamente.");
                window.location.href = "/login";
                return false;
            }
            else if (req.ok) {
                let data = await req.json()
                let acessToken = data.acessToken
                let refreshToken = data.refreshToken
                if (acessToken && refreshToken) {
                    localStorage.setItem("acessToken", acessToken)
                    localStorage.setItem("refreshToken", refreshToken)
                    return true
                }
            }
            return false
        } catch (err) {
            showPopUp("Erro em processar seu login, por favor tente relogar") //erro na tratativa junto ao JWT
            return false
        }
    }
    return false
}

// ---- Modal de Favoritar com Anotação ----

let currentFavoriteUrl = null
let currentFavoriteImg = null
let currentFavoriteElement = null
let favoriteAnnotation = ""

const favoriteModal = document.getElementById("favoriteModal")
const confirmFavoriteButton = document.getElementById("confirmFavorite")
const cancelFavoriteButton = document.getElementById("cancelFavorite")
const favoriteAnnotationInput = document.getElementById("favoriteAnnotation")
const annotationCounter = document.getElementById("annotationCounter")
const favoriteProcessing = document.getElementById("favoriteProcessing")
const logoutProcessing = document.getElementById("logoutProcessing")
const annotationBlock = document.getElementById("annotationBlock")

function showFavoriteModal(sheetUrl, imgSrc, element) {
    currentFavoriteUrl = sheetUrl
    currentFavoriteImg = imgSrc
    currentFavoriteElement = element
    favoriteAnnotation = ""
    if (favoriteAnnotationInput) favoriteAnnotationInput.value = ""
    if (annotationCounter) annotationCounter.textContent = "0/80"
    if (favoriteModal) favoriteModal.style.display = "flex"
}

function hideFavoriteModal() {
    if (favoriteModal) favoriteModal.style.display = "none"
    currentFavoriteUrl = null
    currentFavoriteImg = null
    currentFavoriteElement = null
    favoriteAnnotation = ""
    if (favoriteProcessing) favoriteProcessing.style.display = "none"
    if (confirmFavoriteButton) confirmFavoriteButton.style.display = ""
    if (cancelFavoriteButton) cancelFavoriteButton.style.display = ""
    if (annotationBlock) annotationBlock.style.display = ""
}

if (favoriteAnnotationInput) {
    favoriteAnnotationInput.addEventListener("input", () => {
        const len = favoriteAnnotationInput.value.length
        if (annotationCounter) annotationCounter.textContent = `${len}/80`
        favoriteAnnotation = favoriteAnnotationInput.value
    })
}

if (favoriteModal) {
    favoriteModal.addEventListener("click", (e) => {
        if (e.target === favoriteModal) {
            hideFavoriteModal()
        }
    })
}

if (confirmFavoriteButton) {
    confirmFavoriteButton.addEventListener("click", async () => {
        if (!currentFavoriteUrl || !currentFavoriteElement) return
        if (confirmFavoriteButton) confirmFavoriteButton.style.display = "none"
        if (cancelFavoriteButton) cancelFavoriteButton.style.display = "none"
        if (annotationBlock) annotationBlock.style.display = "none"
        if (favoriteProcessing) favoriteProcessing.style.display = "block"
        currentFavoriteElement.classList.add("processing")
        if (favoriteModal) favoriteModal.style.display = "none"
        const annotationText = favoriteAnnotation ? favoriteAnnotation.trim() : "";
        showPopUp("Favoritando...")
        console.log(annotationText)
        try {
            let postReq = await fetchComAuth(`${url}/favorites`, {
                method: "POST",
                body: JSON.stringify({
                    url: currentFavoriteUrl,
                    href: currentFavoriteImg,
                    annotation: annotationText
                })
            })
            if (postReq.ok) {
                showPopUp("Partitura Favoritada!")
                currentFavoriteElement.classList.remove("processing")
                void currentFavoriteElement.offsetWidth;
                currentFavoriteElement.classList.add("favorite")
                currentFavoriteElement.setAttribute("aria-pressed", 'true')
            } else {
                showPopUp("Tente novamente em alguns segundos")
                currentFavoriteElement.classList.remove("favorite")
                currentFavoriteElement.setAttribute("aria-pressed", 'false')
            }
        } catch (err) {
            showPopUp(err)
            currentFavoriteElement.classList.remove("favorite")
            currentFavoriteElement.setAttribute("aria-pressed", 'false')
        }
        hideFavoriteModal()
    })
}

if (cancelFavoriteButton) {
    cancelFavoriteButton.addEventListener("click", () => {
        hideFavoriteModal()
    })
}

//desfavoritar partituras
const unfavoriteModal = document.getElementById("unfavoriteModal")
const unfavoriteModalText = document.getElementById("unfavoriteModalText")
const unfavoriteProcessing = document.getElementById("unfavoriteProcessing")
const confirmUnfavoriteButton = document.getElementById("confirmUnfavorite")
const cancelUnfavoriteButton = document.getElementById("cancelUnfavorite")

let currentUnfavoriteUrl = null
let currentUnfavoriteElement = null

function showUnfavoriteModal(url, element) {
    currentUnfavoriteUrl = url
    currentUnfavoriteElement = element
    unfavoriteModal.style.display = "flex"
}

function hideUnfavoriteModal() {
    if (unfavoriteModal) unfavoriteModal.style.display = "none"
    currentUnfavoriteUrl = null
    currentUnfavoriteElement = null
    if (unfavoriteProcessing) unfavoriteProcessing.style.display = "none"
    if (confirmUnfavoriteButton) confirmUnfavoriteButton.style.display = ""
    if (cancelUnfavoriteButton) cancelUnfavoriteButton.style.display = ""
    if (unfavoriteModalText) unfavoriteModalText.style.display = ""
}

if (unfavoriteModal) {
    unfavoriteModal.addEventListener("click", (e) => {
        if (e.target === unfavoriteModal) {
            hideUnfavoriteModal()
        }
    })
}

if (confirmUnfavoriteButton) {
    confirmUnfavoriteButton.addEventListener("click", async () => {
        if (currentUnfavoriteUrl && currentUnfavoriteElement) {
            if (confirmUnfavoriteButton) confirmUnfavoriteButton.style.display = "none"
            if (cancelUnfavoriteButton) cancelUnfavoriteButton.style.display = "none"
            if (unfavoriteModalText) unfavoriteModalText.style.display = "none"
            if (unfavoriteProcessing) unfavoriteProcessing.style.display = "block"
            setTimeout(() => {
                if (unfavoriteModal) unfavoriteModal.style.display = "none"
                showPopUp("A página será recarregada!")
            }, 1500)
            try {
                let req = await fetchComAuth(`${url}/favorites`, {
                    method: "DELETE",
                    body: JSON.stringify({ url: currentUnfavoriteUrl })
                })
                if (req.ok) {
                    currentUnfavoriteElement.classList.remove("favorite")
                    currentUnfavoriteElement.setAttribute("aria-pressed", 'false');
                    if (window.location.href.includes("favoritesPage")) window.location.reload()
                } else {
                    showPopUp("Tente novamente em alguns segundos")
                    currentUnfavoriteElement.classList.add("favorite")
                    currentUnfavoriteElement.setAttribute("aria-pressed", 'true');
                }
            } catch (err) {
                showPopUp(err)
                currentUnfavoriteElement.classList.add("favorite")
                currentUnfavoriteElement.setAttribute("aria-pressed", 'true')
            }
            hideUnfavoriteModal()
        }
    })
}

if (cancelUnfavoriteButton) {
    cancelUnfavoriteButton.addEventListener("click", () => {
        hideUnfavoriteModal()
    })
}


//Confirmar Logout
const logoutModal = document.getElementById("logoutModal")
const confirmLogoutButton = document.getElementById("confirmLogout")
const cancelLogoutButton = document.getElementById("cancelLogout")
const unsignButton = document.getElementById("navLogout")

if (unsignButton) {
    unsignButton.addEventListener("click", (e) => {
        e.preventDefault()
        if (logoutModal) logoutModal.style.display = "flex"
    })
}

if (logoutModal) {
    logoutModal.addEventListener("click", (e) => {
        if (e.target === logoutModal) {
            logoutModal.style.display = "none"
        }
    })
}

if (confirmLogoutButton) {
    confirmLogoutButton.addEventListener("click", () => {
        if (confirmLogoutButton) confirmLogoutButton.style.display = "none"
        if (cancelLogoutButton) cancelLogoutButton.style.display = "none"
        if (logoutProcessing) logoutProcessing.style.display = "block"
        localStorage.removeItem("acessToken")
        localStorage.removeItem("refreshToken")
        window.location.reload()
    })
}

if (cancelLogoutButton) {
    cancelLogoutButton.addEventListener("click", () => {
        logoutModal.style.display = "none"
    })
}

if (window.location.href.includes("/favoritesPage")) {
    document.addEventListener("DOMContentLoaded", async () => {
        const token = localStorage.getItem("acessToken");
        if (!token) {
            window.location.href = "/login";
            return;
        }

        const contentBlock = document.getElementById("content");
        const loading = document.getElementById("loading");

        loading.style.display = "block";

        try {
            const response = await fetchComAuth(`${url}/checkFavorites`, {
                method: "GET"
            });
            const data = await response.json();
            if (response.ok && data.favoritos.length == 0) {
                contentBlock.innerHTML = "<p class=\"infoMessage\">Você ainda não tem músicas favoritas.</p>";
            } else if (response.ok && data.favoritos.length != 0) {
                console.log(data.favoritos)
                if (data.favoritos && data.favoritos.length > 0) {
                    data.favoritos.forEach(dices => {
                        let sheetUrl = dices[0]
                        let imgHref = dices[1]
                        let annotation = dices[2]
                        let wrapper = document.createElement("div")
                        wrapper.classList.add("favorite-item")
                        let showcase = document.createElement("div");
                        let link = document.createElement("a");
                        link.setAttribute("target", "_blank");
                        let img = document.createElement("img");
                        let favoriteIcon = document.createElement("div");
                        favoriteIcon.classList.add("favIcon", "favorite");
                        favoriteIcon.setAttribute("aria-pressed", "true");
                        showcase.classList.add("showcase");
                        img.classList.add("score-img");
                        img.src = imgHref
                        link.href = sheetUrl;
                        link.setAttribute("data-url", url);
                        link.appendChild(img);
                        showcase.appendChild(link);
                        showcase.appendChild(favoriteIcon);

                        if (annotation && annotation.trim() !== "") {
                            let annotationToggle = document.createElement("button")
                            annotationToggle.classList.add("annotation-toggle")
                            annotationToggle.textContent = "Anotações"

                            let annotationTooltip = document.createElement("div")
                            annotationTooltip.classList.add("annotation-tooltip")
                            annotationTooltip.textContent = annotation

                            let hideTimeout = null

                            annotationToggle.addEventListener("click", () => {
                                if (annotationTooltip.classList.contains("visible")) {
                                    annotationTooltip.classList.remove("visible")
                                    if (hideTimeout) clearTimeout(hideTimeout)
                                    return
                                }
                                document.querySelectorAll(".annotation-tooltip.visible").forEach(t => t.classList.remove("visible"))
                                annotationTooltip.classList.add("visible")
                            })

                            annotationTooltip.addEventListener("mouseenter", () => {
                                if (hideTimeout) clearTimeout(hideTimeout)
                            })

                            annotationTooltip.addEventListener("mouseleave", () => {
                                hideTimeout = setTimeout(() => {
                                    annotationTooltip.classList.remove("visible")
                                }, 1500)
                            })

                            annotationToggle.addEventListener("mouseleave", () => {
                                hideTimeout = setTimeout(() => {
                                    annotationTooltip.classList.remove("visible")
                                }, 1500)
                            })

                            annotationToggle.addEventListener("mouseenter", () => {
                                if (hideTimeout) clearTimeout(hideTimeout)
                            })

                            showcase.appendChild(annotationToggle)
                            showcase.appendChild(annotationTooltip)
                        }

                        wrapper.appendChild(showcase);
                        contentBlock.appendChild(wrapper);

                        favoriteIcon.addEventListener("click", (e) => {
                            showUnfavoriteModal(sheetUrl, e.target);
                        });
                    });
                }
            } else if (response.status === 404) {
                contentBlock.innerHTML = `<p class=\"infoMessage\">Erro no registro! tente relogar</p>`;
            } else {
                contentBlock.innerHTML = `<p class=\"infoMessage\">Erro no servidor, por favor tente novamente em alguns minutos</p>`;
            }
        } catch (error) {
            contentBlock.innerHTML = `<p class=\"infoMessage\">Ocorreu um erro: ${error.message}</p>`;
        } finally {
            loading.style.display = "none";
        }
    });
}

const allowed = [
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

// Lógica para pegar musica unica
function obterIdUnicoMidia(url) {
    if (!url) return "";

    try {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname.toLowerCase();
        const pathname = urlObj.pathname;

        if (hostname.includes("youtube.com") || hostname.includes("youtu.be")) {
            if (hostname.includes("youtu.be")) return pathname.replace("/", "");
            const videoId = urlObj.searchParams.get("v");
            if (videoId) return videoId;
            const partes = pathname.split("/");
            return partes[partes.length - 1];
        }

        if (hostname.includes("musescore.com")) {
            const match = pathname.match(/\/scores\/(\d+)/);
            return match ? `musescore-${match[1]}` : pathname;
        }

        if (hostname.includes("musicnotes.com")) {
            const partes = pathname.split("/");
            return `musicnotes-${partes[partes.length - 1]}`;
        }

        if (hostname.includes("sheetmusicdirect.com")) {
            const partes = pathname.filter(Boolean);
            return `smd-${partes[partes.length - 1]}`;
        }

        if (hostname.includes("scribd.com")) {
            const match = pathname.match(/\/document\/(\d+)/);
            return match ? `scribd-${match[1]}` : pathname;
        }

        const partesPath = pathname.split("/").filter(p => p.trim() !== "");
        if (partesPath.length > 0) {
            const termoUnico = partesPath[partesPath.length - 1];

            const provedor = allowed.find(site => hostname.includes(site)) || "generico";
            return `${provedor}-${termoUnico}`;
        }

        return url.split('?')[0].replace(/\/$/, "").toLowerCase().trim();

    } catch (e) {
        return url.split('?')[0].replace(/\/$/, "").toLowerCase().trim();
    }
}

const sendBtn = document.getElementById("send")
if (sendBtn) sendBtn.addEventListener("click", async (e) => {
    e.preventDefault()
    if (dice.value !== "") {
        clean("content")
        loading.style.display = "block"
        try {
            const req = await fetch(`${url}/images?q=${encodeURIComponent(dice.value.trim())}&filter=${instruments}`)
            const dices = await req.json();
            if (dices.statusCode === 404) {
                let infoText = document.createElement("p")
                infoText.classList.add("infoMessage")
                infoText.textContent = `Resultados Insuficientes para: ${dices.data["pesquisa"]}`
                contentBlock.appendChild(infoText)
                showPopUp("Tente adicionar ou remover elementos da pesquisa.")
                clean("afterSearch")
                return
            }
            if (dices.statusCode === 500) {
                showPopUp("Erro, por favor tente novamente em alguns minutos!")
                return
            }
            clean("afterSearch")
            const idsProcessados = new Set();
            for (const key in dices.data) {
                let resultBlock = document.createElement("div")
                resultBlock.classList.add("result-block")
                let title = document.createElement("span")
                let text = document.createTextNode(key)
                title.appendChild(text)
                title.classList.add("source-title")
                contentBlock.appendChild(title)
                dices.data[key].forEach((sheet, i) => {
                    const idMidiaAtual = obterIdUnicoMidia(sheet["url"]);
                    if (idMidiaAtual !== "" && idsProcessados.has(idMidiaAtual)) {
                        return
                    }
                    if (idMidiaAtual !== "") {
                        idsProcessados.add(idMidiaAtual);
                    }
                    let showcase = document.createElement("div")
                    let link = document.createElement("a")
                    link.setAttribute("target", "_blank")
                    let img = document.createElement("img")
                    let favoriteIcon = document.createElement("div")
                    favoriteIcon.classList.add("favIcon", `${key}${i}`)
                    showcase.classList.add("showcase")
                    img.classList.add("score-img")
                    img.src = sheet["img"]
                    link.href = sheet["url"]
                    link.setAttribute("data-url", sheet["url"])
                    link.appendChild(img)
                    showcase.appendChild(link)
                    showcase.appendChild(favoriteIcon)
                    resultBlock.appendChild(showcase)
                    contentBlock.appendChild(resultBlock)
                })
            }
            const showcases = document.querySelectorAll(".showcase")
            const token = localStorage.getItem("acessToken")
            if (!token) {
                clean("afterSearch")
                showcases.forEach(swhocase => {
                    let favoriteIcon = swhocase.children[1]
                    favoriteIcon.addEventListener("click", (e) => {
                        showPopUp("Você precisa realizar Login para favoritar")
                    })
                })
                return showPopUp("Considere fazer seu login para poder favoritar")
            }
            if (showcases.length > 0) {
                let req = await fetchComAuth(`${url}/checkFavorites`, {
                    method: "GET",
                })
                if (req.ok) {
                    const res = await req.json()
                    const favoritosIds = (res.favoritos || []).map(([url,]) => obterIdUnicoMidia(url));
                    showcases.forEach(async showcase => {
                        const favoriteIcon = showcase.children[1]
                        const sheetUrl = showcase.children[0].getAttribute("data-url") || showcase.children[0].href
                        const imgSrc = showcase.children[0].children[0].src
                        const idMidiaTela = obterIdUnicoMidia(sheetUrl);

                        if (idMidiaTela !== "" && favoritosIds.includes(idMidiaTela)) {
                            favoriteIcon.classList.add("favorite");
                            favoriteIcon.setAttribute("aria-pressed", 'true');
                        } else {
                            favoriteIcon.classList.remove("favorite");
                            favoriteIcon.setAttribute("aria-pressed", 'false');
                        }

                        favoriteIcon.addEventListener("click", async (e) => {
                            if (e.target.getAttribute("aria-pressed") !== 'true') {
                                showFavoriteModal(sheetUrl, imgSrc, e.target)
                            } else {
                                showUnfavoriteModal(sheetUrl, e.target)
                            }
                        })
                    })
                } else if (req.status === 500) {
                    showPopUp("Erro no servidor, tente novamente em alguns segundos")
                }
            }
        }
        catch (err) {
            showPopUp(err.message)
        }
    }
    else {
        showPopUp("Informe algum valor para realizar uma pesquisa!")
    }

})

if (instrumentsCheckbox.length > 0) {
    instrumentsCheckbox.forEach((checkBox) => {
        checkBox.addEventListener("click", () => {
            if (checkBox.checked) {
                if (!instruments.includes(checkBox.value)) {
                    instruments.push(checkBox.value)
                    filterP.innerText = `Filtros aplicados: ${instruments.join(",")}`
                }
            } else {
                let index = instruments.indexOf(checkBox.value)
                instruments.splice(index, 1)
                if (instruments.length > 0) {
                    filterP.innerText = `Filtros aplicados: ${instruments}`
                } else {
                    filterP.innerText = ""
                }

            }
        })
    })
}

// =============================================
// a partir daqui alguns códigos foram revisados juntamente de um agente de Ia
// =============================================

// ---- Auth Pages: toggle password visibility ----

document.querySelectorAll(".togglePassword").forEach((btn) => {
    btn.addEventListener("click", () => {
        const input = btn.parentElement.querySelector("input")
        if (!input) return
        const isPassword = input.type === "password"
        input.type = isPassword ? "text" : "password"
        btn.textContent = isPassword ? "x" : "👁"
    })
})

// ---- Register Form ----

const registerForm = document.getElementById("registerForm")
if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault()

        const email = document.getElementById("regEmail").value.trim()
        const senha = document.getElementById("regPassword").value
        const confirm = document.getElementById("regConfirm").value

        const oldError = registerForm.querySelector(".authError")
        if (oldError) oldError.remove()

        if (!email) return showAuthError(registerForm, "Preencha o email.")
        if (senha.length < 6) return showAuthError(registerForm, "A senha deve ter no mínimo 6 caracteres.")
        if (senha !== confirm) return showAuthError(registerForm, "As senhas não conferem.")

        showPopUp("Processando dados...")

        try {
            const req = await fetch(`${url}/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userEmail: email,
                    userPass: senha
                })
            })
            const res = await req.json()
            showPopUp(res.message)

        } catch (err) {
            showPopUp("Não foi possivel estabelecer conexão. Tente novamente mais tarde.")
        }
    })
}

// ---- Login Form ----

const loginForm = document.getElementById("loginForm")
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault()

        const email = document.getElementById("loginEmail").value.trim()
        const senha = document.getElementById("loginPassword").value

        const oldError = loginForm.querySelector(".authError")
        if (oldError) oldError.remove()

        if (!email) return showAuthError(loginForm, "Preencha o email.")
        if (!senha) return showAuthError(loginForm, "Preencha a senha.")

        showPopUp("Processando dados...")

        try {
            const req = await fetch(`${url}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userEmail: email,
                    userPass: senha
                })
            })
            const res = await req.json()
            if (res.verificado || res.verificado === false) {
                try {
                    let sendEmail = await fetch(`${url}/sendEmail`, {
                        method: "POST",
                        headers: { "Content-type": "application/json" },
                        body: JSON.stringify({ email })
                    })
                    if (sendEmail.ok) {
                        return showPopUp("Usuario não verificado, enviando novo email de verificação")
                    }
                    else if (sendEmail.status === 404) {
                        showPopUp(sendEmail.message)
                        return
                    }
                } catch (err) {
                    showPopUp("Erro inesperado: ", err)
                }

            }
            if (res.success && res.success !== false) {
                localStorage.setItem("acessToken", res.acessToken)
                localStorage.setItem("refreshToken", res.refreshToken)
                showPopUp("Redirecionando...")
                window.location.href = "/"
            } else {
                return showPopUp("Usuário ou senha incorretos!")
            }
        } catch (err) {
            showPopUp("Erro interno do servidor. Tente novamente mais tarde.")
        }
    })
}

// ---- Helper ----

function showAuthError(form, message) {
    const old = form.querySelector(".authError")
    if (old) old.remove()
    const error = document.createElement("p")
    error.className = "authError"
    error.textContent = message
    form.insertBefore(error, form.querySelector(".authSubmit"))
}

// ---- Diamond Nav Toggle ----

const diamondBtn = document.getElementById("diamondBtn")
const navDropdown = document.getElementById("navDropdown")

if (diamondBtn && navDropdown) {
    diamondBtn.addEventListener("click", (e) => {
        e.stopPropagation()
        navDropdown.classList.toggle("open")
    })

    document.addEventListener("click", (e) => {
        if (!navDropdown.contains(e.target) && e.target !== diamondBtn) {
            navDropdown.classList.remove("open")
        }
    })
}

const navFavorites = document.getElementById("navFavorites")

if (navFavorites) {
    navFavorites.addEventListener("click", async (e) => {
        e.preventDefault()
        let token = localStorage.getItem("acessToken")
        if (token) {
            window.location = `${url}/favoritesPage`
        }
    })
}
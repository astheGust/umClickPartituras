const url = "https://umclickpartituras.onrender.com"
const urlDebug = "http://127.0.0.1:5000"


window.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("mode")) {
        document.getElementById("lightMode").innerText = "Light"
    }
})

const loading = document.getElementById("loading")

document.getElementById("send").addEventListener("click", async (e) => {
    e.preventDefault()
    let dice = document.getElementById("query")
    if (dice.value !== "") {
        const contentBlock = document.getElementById("content")
        contentBlock.innerHTML = ""
        loading.style.display = "block"
        try {
            const res = await fetch(`${urlDebug}/images?q=${encodeURIComponent(dice.value)}&filter=${instruments}`)
            const dices = await res.json();
            console.log(dices)
            for (x in dices.data) {
                let resultBlock = document.createElement("div")
                resultBlock.classList.add("result-block")
                let title = document.createElement("span")
                let text = document.createTextNode(x)
                title.appendChild(text)
                title.classList.add("source-title")
                contentBlock.appendChild(title)
                dices.data[x].forEach((y) => {
                    let showcase = document.createElement("div")
                    let link = document.createElement("a")
                    link.setAttribute("target", "_blank")
                    let img = document.createElement("img")
                    showcase.classList.add("showcase")
                    img.classList.add("score-img")
                    img.src = y["img"]
                    link.href = y["url"]
                    link.appendChild(img)
                    showcase.appendChild(link)
                    resultBlock.appendChild(showcase)
                    contentBlock.appendChild(resultBlock)
                })
            }
            if (dices.statusCode === 206) {
                document.getElementById("content").innerHTML = dices.message
                return
            }
        } catch (err) {
            console.error(err)
        }
        dice.value = ""
        loading.style.display = "none"
    }
    else {
        alert("INFORME ALGUM VALOR PARA CONTINUAR A PESQUISA!")
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

const instrumentsCheckbox = document.querySelectorAll(".instrumentCheckbox")
const filterP = document.getElementById("filterText")
const instruments = []

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
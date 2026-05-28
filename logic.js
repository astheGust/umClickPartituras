const url = "https://umclickpartituras.onrender.com"
const urlDebug = "http://127.0.0.1:5000"
const loading = document.getElementById("loading")
document.getElementById("send").addEventListener("click", async (e) => {
    e.preventDefault()
    let dice = document.getElementById("query")

    if (dice.value !== "") {
        const contentBlock = document.getElementById("content")
        contentBlock.innerHTML = ""
        loading.style.display = "block"
        try {
            const res = await fetch(`${url}/images?q=${encodeURIComponent(dice.value)}`)

            const data = await res.json();

            for (x in data) {
                let resultBlock = document.createElement("div")
                resultBlock.classList.add("result-block")
                let title = document.createElement("span")
                let text = document.createTextNode(x)
                title.appendChild(text)
                title.classList.add("source-title")
                contentBlock.appendChild(title)
                data[x].forEach((y) => {
                    let showcase = document.createElement("div")
                    let link = document.createElement("a")
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

let active = false
document.getElementById("lightMode").addEventListener("click",()=>{
    active = !active
    document.body.classList.toggle("dark")
    if(active){
        document.getElementById("lightMode").innerText = "Light"
    }
    else{
        document.getElementById("lightMode").innerText = "Dark"
    }
})

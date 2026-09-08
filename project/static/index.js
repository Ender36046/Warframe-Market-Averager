const searchbar = document.getElementById("searchbar")

let slug = ""

searchbar.addEventListener("input", function(e){
    slug = e.target.value
    const baseURL = window.location.origin
    if(e.key == "Enter"){
        window.location.href = `${baseURL}/items/slug`
    }
    console.log(slug)
})
const searchbar = document.getElementById("searchbar")

let slug = ""

searchbar.addEventListener("input", function(e){
    slug = slug + e.target.value
    console.log(slug)
})
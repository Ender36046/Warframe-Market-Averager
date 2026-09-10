const searchbar = document.getElementById("searchbar")

let slug = ""

searchbar.addEventListener("keydown", function(e){
    slug = e.target.value;
    const baseURL = window.location.origin;
    if(e.key == "Enter"){
        newInput = formatInput(slug)
        window.location.href = `${baseURL}/items/${newInput}`;
    }
    console.log(slug);
})

function formatInput(userInput){
    userInput = userInput.toLowerCase().trim();
    newInput = userInput.replaceAll(" ", "_");
    return newInput
}

async function ask() {
    let question = document.getElementById("question").value;

    let res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question
        })
    });

    let data = await res.json();

    document.getElementById("response").innerText = data.answer;
}

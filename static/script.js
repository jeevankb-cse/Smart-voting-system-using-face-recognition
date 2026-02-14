async function identifyServer() {
    const resp = await fetch("/identify");
    return resp.json();
}

function showStatus(text, color = "black") {
    const msg = document.getElementById("statusMsg");
    msg.textContent = text;
    msg.style.color = color;
}

async function startVote(party) {
    showStatus("Scanning face... Please look at the camera.", "darkorange");

    let ident;
    try {
        ident = await identifyServer();
    } catch (e) {
        showStatus("Error contacting server for identification.", "red");
        alert("Error contacting server.");
        return;
    }

    if (ident.status !== "ok") {
        showStatus(ident.message || "Identification failed.", "red");
        alert(ident.message || "Identification failed.");
        return;
    }

    const label = ident.label || "Unknown";

    if (label === "Unknown") {
        showStatus("Face not recognized. Contact admin.", "red");
        alert("Face not recognized. Please register or contact admin.");
        return;
    }

    // Ask user to confirm the identified Aadhaar (or allow manual override)
    const confirmMsg = `Identified Aadhaar: ${label}\nDo you confirm to cast vote as this Aadhaar? Press OK to confirm or Cancel to enter Aadhaar manually.`;
    const confirmed = confirm(confirmMsg);

    let voterToSend = label;
    if (!confirmed) {
        const manual = prompt("Enter Aadhaar number (manual):");
        if (!manual) {
            showStatus("Voting canceled — Aadhaar required.", "red");
            return;
        }
        voterToSend = manual.trim();
    }

    // Send vote
    try {
        const r = await fetch("/vote", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter: voterToSend, party: party })
        });
        const data = await r.json();
        if (data.status === "success") {
            showStatus(data.message, "green");
            alert("✅ " + data.message);
        } else {
            showStatus(data.message, "red");
            alert("⚠️ " + data.message);
        }
    } catch (e) {
        showStatus("Error sending vote.", "red");
        console.error(e);
        alert("Error sending vote.");
    }
}

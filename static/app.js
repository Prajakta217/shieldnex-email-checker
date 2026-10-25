const emailsInput = document.getElementById("emails");
const checkBtn = document.getElementById("checkBtn");
const clearBtn = document.getElementById("clearBtn");
const message = document.getElementById("message");
const resultsSection = document.getElementById("resultsSection");
const resultsBody = document.getElementById("resultsBody");


function getStatusClass(status) {
if (status === "Likely bounce") return "bounce";
if (status === "Likely delivered") return "delivered";
return "unknown";
}

function addCell(row, text) {
const cell = document.createElement("td");
cell.textContent = text;
row.appendChild(cell);
return cell;
}

function displayResults(data) {
resultsBody.replaceChildren();

data.results.forEach(item => {
const row = document.createElement("tr");

addCell(row, item.email);

const statusCell = addCell(row, "");
const badge = document.createElement("span");
badge.className = getStatusClass(item.status);
badge.textContent = item.status;
statusCell.appendChild(badge);

addCell(row, item.reason);
resultsBody.appendChild(row);
});

document.getElementById("totalCount").textContent =
data.counts.total;
document.getElementById("deliveredCount").textContent =
data.counts.likely_delivered;
document.getElementById("bounceCount").textContent =
data.counts.likely_bounce;
document.getElementById("unknownCount").textContent =
data.counts.unknown;

resultsSection.classList.remove("hidden");
}

checkBtn.addEventListener("click", async () => {
message.textContent = "";
checkBtn.disabled = true;
checkBtn.textContent = "Checking...";

try {
const response = await fetch("/api/check", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({
emails: emailsInput.value
})
});

const data = await response.json();

if (!response.ok) {
throw new Error(data.error || "The check failed.");
}

displayResults(data);
message.textContent =
"Check complete. Results are estimates, not delivery guarantees.";

} catch (error) {
message.textContent =
error.message || "Something went wrong. Please try again.";
} finally {
checkBtn.disabled = false;
checkBtn.textContent = "Check emails";
}
});

clearBtn.addEventListener("click", () => {
emailsInput.value = "";
resultsBody.replaceChildren();
resultsSection.classList.add("hidden");
message.textContent = "";
emailsInput.focus();
});
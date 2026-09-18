const jobText = document.getElementById("jobText");
const charCount = document.getElementById("charCount");


jobText.addEventListener("input", function () {

    charCount.textContent =
        `${jobText.value.length} characters`;

});


async function analyzeJob() {

    const text = jobText.value.trim();

    if (!text) {

        alert("Please paste a job description first.");

        return;

    }


    const loading =
        document.getElementById("loading");

    const results =
        document.getElementById("results");

    const button =
        document.getElementById("analyzeBtn");


    loading.classList.remove("hidden");

    results.classList.add("hidden");

    button.disabled = true;


    try {

        const response = await fetch("/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })

        });


        const data = await response.json();


        if (!response.ok) {

            alert(data.error || "Something went wrong.");

            return;

        }


        // Risk score

        document.getElementById("riskScore")
            .textContent = data.risk_score + "/100";


        document.getElementById("mlScore")
            .textContent = data.scam_probability + "%";


        document.getElementById("prediction")
            .textContent = data.prediction;


        // Progress bar

        document.getElementById("progressBar")
            .style.width = data.risk_score + "%";


        // Risk badge

        const badge =
            document.getElementById("resultBadge");

        badge.textContent =
    data.risk_level + " RISK";

badge.className = "";

if (data.risk_level === "HIGH") {
    badge.classList.add("risk-high");
}
else if (data.risk_level === "MEDIUM") {
    badge.classList.add("risk-medium");
}
else {
    badge.classList.add("risk-low");
}


        // Indicators

        const indicatorContainer =
            document.getElementById("indicators");

        indicatorContainer.innerHTML = "";


        if (data.indicators.length === 0) {

            indicatorContainer.innerHTML =
                `<div class="no-indicators">
                    ✓ No major suspicious indicators detected
                </div>`;

        } else {

            data.indicators.forEach(indicator => {

                const div =
                    document.createElement("div");

                div.className = "indicator";

                div.textContent = "⚠ " + indicator;

                indicatorContainer.appendChild(div);

            });

        }


        // Safety message

        const message =
            document.getElementById("safetyMessage");


        if (data.risk_level === "HIGH") {

            message.textContent =
                "⚠ This posting contains multiple suspicious signals. Avoid sending money or sensitive personal information until the employer is independently verified.";

        }

        else if (data.risk_level === "MEDIUM") {

            message.textContent =
                "⚠ Some suspicious signals were detected. Verify the company, recruiter and job posting through official channels before proceeding.";

        }

        else {

            message.textContent =
                "✓ No major scam signals were detected. Still verify the employer independently before sharing sensitive information.";

        }


        results.classList.remove("hidden");

        results.scrollIntoView({
            behavior: "smooth"
        });

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server."
        );

    }

    finally {

        loading.classList.add("hidden");

        button.disabled = false;

    }

}


function clearText() {

    jobText.value = "";

    charCount.textContent =
        "0 characters";

    document.getElementById("results")
        .classList.add("hidden");

}
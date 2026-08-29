(function () {
    "use strict";

    const script = document.currentScript;

    if (!script) {
        console.error("Widget script could not find itself.");
        return;
    }

    const apiKey = script.getAttribute("data-api-key");

    if (!apiKey) {
        console.error("Widget API key is missing.");
        return;
    }

    const apiBaseUrl =
        script.getAttribute("data-api-url") ||
        "http://localhost:8000";

    async function loadWidget() {
        try {
            const response = await fetch(
                `${apiBaseUrl}/api/public/widgets/${apiKey}`
            );

            if (!response.ok) {
                throw new Error(
                    `Widget API returned ${response.status}`
                );
            }

            const widget = await response.json();

            renderWidget(widget);
        } catch (error) {
            console.error("Failed to load widget:", error);
        }
    }

    function renderWidget(widget) {
        const config = widget.config || {};

        const container = document.createElement("div");

        container.id = `flyrank-widget-${widget.id}`;

        container.style.position = "fixed";
        container.style.bottom = "20px";
        container.style.right = "20px";
        container.style.width = "320px";
        container.style.padding = "20px";
        container.style.background = "#ffffff";
        container.style.border = "1px solid #ddd";
        container.style.borderRadius = "12px";
        container.style.boxShadow =
            "0 4px 20px rgba(0, 0, 0, 0.15)";
        container.style.fontFamily =
            "Arial, sans-serif";
        container.style.zIndex = "999999";

        const title = document.createElement("h3");

        title.textContent =
            config.title || widget.name;

        title.style.marginTop = "0";

        container.appendChild(title);

        const fields = Array.isArray(config.fields)
            ? config.fields
            : ["name", "email", "message"];

        fields.forEach(function (field) {
            const label = document.createElement("label");

            label.textContent =
                field.charAt(0).toUpperCase() +
                field.slice(1);

            label.style.display = "block";
            label.style.marginTop = "10px";
            label.style.marginBottom = "4px";

            const input = document.createElement(
                field === "message"
                    ? "textarea"
                    : "input"
            );

            input.name = field;
            input.placeholder = label.textContent;

            input.style.width = "100%";
            input.style.boxSizing = "border-box";
            input.style.padding = "8px";
            input.style.border = "1px solid #ccc";
            input.style.borderRadius = "6px";

            container.appendChild(label);
            container.appendChild(input);
        });

        const button = document.createElement("button");

        button.textContent =
            config.button_text || "Submit";

        button.style.marginTop = "15px";
        button.style.width = "100%";
        button.style.padding = "10px";
        button.style.border = "none";
        button.style.borderRadius = "6px";
        button.style.cursor = "pointer";

        button.addEventListener("click", function () {
            alert(
                config.success_message ||
                "Thank you! Your submission has been received."
            );
        });

        container.appendChild(button);

        document.body.appendChild(container);
    }

    loadWidget();
})();

"use strict";

// ─────────────────────────────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────────────────────────────
const API_URL         = "http://127.0.0.1:5000";
const MAX_SIZE_BYTES  = 5 * 1024 * 1024;   // 5MB
const ALLOWED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];


// ─────────────────────────────────────────────────────────────────────
// DOM REFERENCES
// ─────────────────────────────────────────────────────────────────────
const dropzone        = document.getElementById("dropzone");
const fileInput       = document.getElementById("file-input");
const preview         = document.getElementById("preview");
const previewImg      = document.getElementById("preview-img");
const previewName     = document.getElementById("preview-name");
const previewSize     = document.getElementById("preview-size");
const clearBtn        = document.getElementById("clear-btn");
const submitBtn       = document.getElementById("submit-btn");
const resultSection   = document.getElementById("result-section");
const resultBadge     = document.getElementById("result-badge");
const resultFilename  = document.getElementById("result-filename");
const resultLabel     = document.getElementById("result-label");
const resultProb      = document.getElementById("result-prob");
const resultDecision  = document.getElementById("result-decision");
const resetBtn        = document.getElementById("reset-btn");
const loader          = document.getElementById("loader");
const errorBanner     = document.getElementById("error-banner");
const errorMessage    = document.getElementById("error-message");


// ─────────────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────────────
let selectedFile = null;


// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────
function formatBytes(bytes) {
    if (bytes < 1024)        return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function showError(message) {
    errorBanner.hidden  = false;
    errorMessage.textContent = message;
}

function hideError() {
    errorBanner.hidden  = true;
    errorMessage.textContent = "";
}

function showLoader() {
    loader.hidden        = false;
    submitBtn.disabled   = true;
}

function hideLoader() {
    loader.hidden        = true;
    submitBtn.disabled   = false;
}

function resetUI() {
    // File state
    selectedFile         = null;
    fileInput.value      = "";

    // Hide sections
    preview.hidden       = true;
    resultSection.hidden = true;
    loader.hidden        = true;

    // Reset preview content
    previewImg.src       = "";
    previewName.textContent = "";
    previewSize.textContent = "";

    // Reset result content
    resultBadge.textContent  = "";
    resultBadge.className    = "result__badge";
    resultFilename.textContent = "";
    resultLabel.textContent  = "";
    resultProb.textContent   = "";
    resultDecision.textContent = "";

    // Reset button and errors
    submitBtn.disabled   = true;
    hideError();
}


// ─────────────────────────────────────────────────────────────────────
// FILE VALIDATION
// ─────────────────────────────────────────────────────────────────────
function validateFile(file) {
    if (!ALLOWED_TYPES.includes(file.type)) {
        return "Invalid file type. Please upload a JPG or PNG image.";
    }
    if (file.size > MAX_SIZE_BYTES) {
        return `File too large. Maximum size is 5MB. Your file is ${formatBytes(file.size)}.`;
    }
    return null;
}


// ─────────────────────────────────────────────────────────────────────
// FILE SELECTION
// ─────────────────────────────────────────────────────────────────────
function handleFileSelect(file) {
    console.log("File received:", file.name, file.type, file.size);
    hideError();

    const error = validateFile(file);
    if (error) {
        showError(error);
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src  = e.target.result;
        preview.hidden  = false;
    };
    reader.readAsDataURL(file);

    // Fill preview info
    previewName.textContent = file.name;
    previewSize.textContent = formatBytes(file.size);

    // Hide result if showing from previous run
    resultSection.hidden = true;

    // Enable submit
    submitBtn.disabled = false;
}


// ─────────────────────────────────────────────────────────────────────
// DRAG AND DROP
// ─────────────────────────────────────────────────────────────────────
dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone--active");
});

dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dropzone--active");
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dropzone--active");

    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
});

dropzone.addEventListener("click", (e) => {
    // Don't trigger if clicking the label or input directly
    if (e.target === fileInput || e.target.tagName === "LABEL") return;
    fileInput.click();
});


// ─────────────────────────────────────────────────────────────────────
// FILE INPUT CHANGE
// ─────────────────────────────────────────────────────────────────────
fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    } else {
        console.log("No file found in input");
    }
});


// ─────────────────────────────────────────────────────────────────────
// CLEAR BUTTON
// ─────────────────────────────────────────────────────────────────────
clearBtn.addEventListener("click", () => {
    resetUI();
});


// ─────────────────────────────────────────────────────────────────────
// SUBMIT
// ─────────────────────────────────────────────────────────────────────
submitBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    hideError();
    showLoader();
    resultSection.hidden = true;

    // Build form data
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            body:   formData
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Something went wrong. Please try again.");
            return;
        }

        displayResult(data);

    } catch (err) {
        showError("Could not connect to the server. Make sure the app is running.");
    } finally {
        hideLoader();
    }
});


// ─────────────────────────────────────────────────────────────────────
// DISPLAY RESULT
// ─────────────────────────────────────────────────────────────────────
function displayResult(data) {
    // Badge
    const badgeMap = {
        "ACCEPT":        { text: "✓  ACCEPTED",      cls: "result__badge--accept" },
        "REJECT":        { text: "✕  REJECTED",       cls: "result__badge--reject" },
        "MANUAL_REVIEW": { text: "⚠  MANUAL REVIEW",  cls: "result__badge--review" }
    };

    const badge = badgeMap[data.decision] ?? {
        text: data.decision,
        cls:  "result__badge--review"
    };

    resultBadge.textContent = badge.text;
    resultBadge.className   = `result__badge ${badge.cls}`;

    // Details
    resultFilename.textContent = data.filename;
    resultLabel.textContent    = data.label ?? "—";
    resultProb.textContent     = data.prob !== null
        ? `${(data.prob * 100).toFixed(1)}%`
        : "—";
    resultDecision.textContent = data.decision;

    // Show result section
    resultSection.hidden = false;
    resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ─────────────────────────────────────────────────────────────────────
// RESET BUTTON
// ─────────────────────────────────────────────────────────────────────
resetBtn.addEventListener("click", () => {
    resetUI();
});
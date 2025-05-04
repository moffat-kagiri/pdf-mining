# Install system dependencies
choco install poppler tesseract -y

# Set environment variables
[System.Environment]::SetEnvironmentVariable(
    "POPPLER_PATH",
    "C:\Program Files\poppler-25.04.0\Library\bin",
    [System.EnvironmentVariableTarget]::User
)

[System.Environment]::SetEnvironmentVariable(
    "TESSERACT_PATH",
    "C:\Program Files\Tesseract-OCR",
    [System.EnvironmentVariableTarget]::User
)

Write-Host "Please restart your terminal to apply changes"
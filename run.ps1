#!/usr/bin/env pwsh

# This script is used to run the application
. .\.venv\Scripts\Activate.ps1

# Load environment variables
$envVars = Get-Content .env | ForEach-Object {
    if ($_ -match "^\s*([^#\s]+)\s*=\s*(.*)\s*$") {
        $name = $matches[1]
        $value = $matches[2]
        [System.Environment]::SetEnvironmentVariable($name, $value)
    }
}

# Run the Python script
python auslander.py
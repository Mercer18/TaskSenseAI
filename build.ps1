$ErrorActionPreference = "Stop"

Write-Host "Installing requirements..."
pip install -r requirements.txt
pip install pyinstaller

Write-Host "Building TaskSenseAI executable..."
pyinstaller --noconfirm --onedir --windowed --add-data "tasksenseai/data;tasksenseai/data" --add-data "tasksenseai/models;tasksenseai/models" --name "TaskSenseAI" .\run_tasksense.py

Write-Host "Build complete! Executable is located in the dist\TaskSenseAI\ folder."

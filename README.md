# TaskSenseAI

TaskSenseAI is a Python desktop task manager built with PyQt6 that tracks tasks, logs behavior, and uses a machine learning model to estimate procrastination risk.

## Features

- Create and manage tasks through a desktop GUI
- View dashboard, task list, analytics, settings, and AI insights pages
- Store task and prediction data in a local SQLite database
- Train or load a procrastination-risk model from project data
- Generate predictions based on delay, ignored reminders, and completion time

## Project Structure

- `main.py` - app entry point
- `gui/` - PyQt6 interface pages
- `modules/` - AI, reminders, behavior tracking, and task logic
- `database/` - SQLite setup and DB access
- `data/` - training data used by the model
- `models/` - saved machine learning model
- `assets/` - static app assets

## Requirements

- Python 3.13 recommended
- PyQt6
- numpy
- pandas
- scikit-learn

## Run

```powershell
python main.py
```

## Notes

- The SQLite database file is ignored in Git so each machine can create its own local data.
- The trained model file is included because the app uses it directly.

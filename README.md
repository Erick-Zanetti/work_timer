# Work Timer

A simple, beautiful floating timer widget for tracking work/task intervals.
Built with Python and PyQt5, featuring a Nord-themed UI.

## Features

- **Multiple Timers**: Track up to 3 tasks simultaneously.
- **Exclusive Timing**: Only one timer runs at a time (switching automatically pauses others).
- **Floating Window**: Stays on top of other windows for easy visibility.
- **Nord Theme**: Clean, modern, and easy on the eyes.
- **Add Time**: Easily adjust timers by adding/removing time (e.g., `+10` mins, `+1h`).

## Running the Application

### From Source
1. Install dependencies:
   ```bash
   pip install PyQt5
   ```
2. Run the script:
   ```bash
   python work_timer.py
   ```

### Executable
You can find the standalone `.exe` file in the `dist/` directory.

## Controls

- **+**: Add a new timer.
- **✕**: Close the application.
- **▶ / ⏸**: Start or Pause a timer.
- **+T**: Add time to the timer (Supports formats like `5` for minutes, `1h`, `30s`).
- **↺**: Reset timer to 00:00:00.

## License

MIT

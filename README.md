# Auto Clicker

A lightweight, customizable auto clicker utility written in Python. This tool allows you to automate mouse clicks at specified intervals, toggled with keyboard or mouse buttons.

## Features

- Adjustable clicks per second (CPS)
- Toggle clicking on/off with a keyboard key
- Optional mouse button toggling
- Simple command-line interface for customization

## Requirements

- Python 3.6 or higher
- `pynput` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/auto_clicker.git
   cd auto_clicker
   ```

2. Install the required dependencies:
   ```bash
   pip install pynput
   ```

## Usage

Run the auto clicker with default settings:

```bash
python -m auto_clicker.cli
```

### Command Line Arguments

- `--cps`: Set clicks per second (default: 500)
- `--key`: Set the keyboard key to toggle clicking (default: 'c')
- `--mouse`: Set a mouse button to toggle clicking (options: 'left', 'right', 'middle')

### Examples

```bash
# Run with 1000 clicks per second
python -m auto_clicker.cli --cps 1000

# Use the 'x' key to toggle clicking
python -m auto_clicker.cli --key x

# Use the right mouse button to toggle clicking
python -m auto_clicker.cli --mouse right

# Combine multiple options
python -m auto_clicker.cli --cps 200 --key v --mouse middle
```

## Controls

- Press the toggle key (default: 'C') to start/stop clicking
- Use the configured mouse button (if set) to start/stop clicking
- Press ESC to exit the program

## Project Structure

```markdown
auto_clicker/
├── auto_clicker/       # Main package
│   ├── __init__.py     # Package initialization
│   ├── clicker.py      # Core functionality
│   └── cli.py          # Command-line interface
├── tests/              # Test suite
│   ├── __init__.py
│   └── test_clicker.py
├── setup.py            # Installation configuration
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```

## License

[MIT License](LICENSE)
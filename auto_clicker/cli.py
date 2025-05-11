"""Command-line interface for the auto clicker."""

import argparse
from .clicker import AutoClicker

def parse_args():
    parser = argparse.ArgumentParser(
        description="Auto Clicker - A configurable tool to automate mouse clicks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_clicker.py                      # Run with default settings (500 CPS, toggle with 'c')
  python auto_clicker.py --cps 10             # Run with 10 clicks per second
  python auto_clicker.py --key space          # Toggle clicking with spacebar
  python auto_clicker.py --mouse right        # Toggle clicking with right mouse button
  python auto_clicker.py --cps 50 --key f     # 50 CPS, toggle with 'f' key

Special Keys:
  For special keys, use their name: ctrl, alt, shift, space, tab, esc, etc.

Mouse Buttons:
  Valid mouse buttons: left, right, middle
        """
    )
    parser.add_argument("--cps", type=float, default=500, 
                       help="Clicks per second (default: 500). Use lower values like 5-20 for most applications.")
    parser.add_argument("--key", type=str, default="c", 
                       help="Key to toggle clicking (default: 'c'). Can be a character or special key name.")
    parser.add_argument("--mouse", type=str, default=None, 
                      help="Mouse button to toggle clicking (options: 'left', 'right', 'middle', default: None)")
    
    return parser.parse_args()

def main():
    args = parse_args()
    auto_clicker = AutoClicker(cps=args.cps, toggle_key=args.key, toggle_mouse_button=args.mouse)
    auto_clicker.start()

if __name__ == "__main__":
    main()
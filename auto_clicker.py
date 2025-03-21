#!/usr/bin/env python3

from pynput import keyboard, mouse
import threading
import time
import argparse

class AutoClicker:
    def __init__(self, cps=500, toggle_key='c', toggle_mouse_button=None):
        self.mouse_controller = mouse.Controller()
        self.is_clicking = False
        self.click_thread = None
        self.running = True
        
        # Validate CPS
        try:
            self.cps = float(cps)
            if self.cps <= 0:
                raise ValueError("CPS must be positive")
            self.click_interval = 1.0 / self.cps  # in seconds
        except ValueError:
            print(f"Invalid CPS value: {cps}. Using default of 500.")
            self.cps = 500
            self.click_interval = 0.002
        
        # Configure toggle key
        if hasattr(keyboard.Key, toggle_key):
            self.toggle_key = getattr(keyboard.Key, toggle_key)
            self.toggle_key_name = toggle_key.upper()
        else:
            self.toggle_key = toggle_key
            self.toggle_key_name = toggle_key.upper()
        
        # Configure toggle mouse button
        self.toggle_mouse_button = None
        self.toggle_mouse_button_name = "None"
        if toggle_mouse_button:
            if hasattr(mouse.Button, toggle_mouse_button):
                self.toggle_mouse_button = getattr(mouse.Button, toggle_mouse_button)
                self.toggle_mouse_button_name = toggle_mouse_button.upper()
            else:
                print(f"Invalid mouse button: {toggle_mouse_button}. Mouse toggling disabled.")
             
        print(f"Click interval: {self.click_interval:.6f} seconds ({self.cps} CPS)")

    def simulate_mouse_click(self):
        """
        Simulates mouse clicks at regular intervals based on CPS setting.
        """
        while self.is_clicking and self.running:
            self.mouse_controller.click(mouse.Button.left, 1)
            time.sleep(self.click_interval)

    def on_press(self, key):
        """
        Handles key press events.
        """
        try:
            # Handle character keys
            if hasattr(key, 'char') and key.char == self.toggle_key:
                self.toggle_clicking()
            # Handle special keys
            elif key == self.toggle_key:
                self.toggle_clicking()
        except AttributeError:
            pass

    def on_click(self, x, y, button, pressed):
        """
        Handles mouse click events.
        """
        if self.toggle_mouse_button and button == self.toggle_mouse_button and pressed:
            self.toggle_clicking()

    def toggle_clicking(self):
        """Toggle the clicking state"""
        self.is_clicking = not self.is_clicking
        if self.is_clicking:
            self.click_thread = threading.Thread(target=self.simulate_mouse_click)
            self.click_thread.daemon = True  # Thread will exit when program exits
            self.click_thread.start()
        print(f"Mouse clicking {'started' if self.is_clicking else 'stopped'}")

    def on_release(self, key):
        """
        Handles key release events.
        """
        if key == keyboard.Key.esc:
            print("Stopping auto clicker")
            self.is_clicking = False
            self.running = False
            return False  # Stop listener

    def start(self):
        """
        Starts the auto clicker with both keyboard and mouse listeners.
        """
        toggle_info = f"Press '{self.toggle_key_name}' to toggle clicking"
        if self.toggle_mouse_button:
            toggle_info += f" or use mouse {self.toggle_mouse_button_name}"
        
        print(f"Starting auto clicker. {toggle_info}. Press ESC to exit.")
        
        # Create both listeners
        keyboard_listener = keyboard.Listener(
            on_press=self.on_press, 
            on_release=self.on_release
        )
        mouse_listener = mouse.Listener(
            on_click=self.on_click
        )
        
        # Start both listeners
        keyboard_listener.start()
        mouse_listener.start()
        
        # Keep the program running until keyboard listener stops
        keyboard_listener.join()
        
        # Stop mouse listener when keyboard listener stops
        mouse_listener.stop()

def parse_args():
    parser = argparse.ArgumentParser(description="Auto Clicker")
    parser.add_argument("--cps", type=float, default=500, help="Clicks per second (default: 500)")
    parser.add_argument("--key", type=str, default="c", help="Key to toggle clicking (default: c)")
    parser.add_argument("--mouse", type=str, default=None, 
                      help="Mouse button to toggle clicking (e.g., 'right', 'middle', default: None)")
    return parser.parse_args()

def main():
    args = parse_args()
    auto_clicker = AutoClicker(cps=args.cps, toggle_key=args.key, toggle_mouse_button=args.mouse)
    auto_clicker.start()

if __name__ == "__main__":
    main()
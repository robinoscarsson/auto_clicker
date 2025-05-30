"""Core auto clicker functionality."""

from pynput import keyboard, mouse
import threading
import time

class AutoClicker:
    def __init__(self, cps=500, toggle_key='c', toggle_mouse_button=None):
        self.mouse_controller = mouse.Controller()
        self.is_clicking = False
        self.click_thread = None
        self.running = True
        
        if cps <= 0:
            print(f"Invalid CPS value: {cps}. Using default CPS of 500.")
            cps = 500

        self.cps = cps
        self.click_interval = 1.0 / cps
        
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
            # Convert to lowercase for case-insensitive comparison
            toggle_mouse_button_lower = toggle_mouse_button.lower()
            if hasattr(mouse.Button, toggle_mouse_button_lower):
                self.toggle_mouse_button = getattr(mouse.Button, toggle_mouse_button_lower)
                self.toggle_mouse_button_name = toggle_mouse_button.upper()
            else:
                print(f"Invalid mouse button: {toggle_mouse_button}. Mouse toggling disabled.")
                print(f"Valid options are: {', '.join([b for b in dir(mouse.Button) if not b.startswith('_')])}")
             
        print(f"Click interval: {self.click_interval:g} seconds ({self.cps} CPS)")

    def simulate_mouse_click(self):
        """
        Simulates mouse clicks with improved timing accuracy.
        """
        next_click_time = time.time()
        while self.is_clicking and self.running:
            current_time = time.time()
            if current_time >= next_click_time:
                self.mouse_controller.click(mouse.Button.left, 1)
                next_click_time = current_time + self.click_interval
            
            # Smaller sleep to reduce CPU usage while maintaining precision
            time.sleep(min(0.001, self.click_interval / 10))

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
        if self.is_clicking:
            # Turning off - just update flag and let thread exit naturally
            self.is_clicking = False
        else:
            # Turning on - create new thread only if needed
            self.is_clicking = True
            if not self.click_thread or not self.click_thread.is_alive():
                self.click_thread = threading.Thread(target=self.simulate_mouse_click)
                self.click_thread.daemon = True
                self.click_thread.start()
    
        print(f"\rMouse clicking {'started' if self.is_clicking else 'stopped'}     ", end="", flush=True)

    def on_release(self, key):
        """
        Handles key release events.
        """
        if key == keyboard.Key.esc:
            print("Stopping auto clicker")
            self.is_clicking = False
            self.running = False
            return False  # Stop listener

    def cleanup(self):
        """Clean up resources before exiting"""
        self.is_clicking = False
        self.running = False
        
        # Wait for click thread to terminate
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=0.2)
            
        # Release controllers if needed
        # (pynput handles most of this automatically)

    def start(self):
        """
        Starts the auto clicker with both keyboard and mouse listeners.
        """

        try:
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
            keyboard_listener.join()
        finally:
            mouse_listener.stop()
            self.cleanup()
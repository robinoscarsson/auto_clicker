"""Core auto clicker functionality."""

from pynput import keyboard, mouse
import threading
import time

class AutoClicker:
    def __init__(self, cps=500, toggle_key='c', toggle_mouse_button=None):
        self.mouse_controller = mouse.Controller()
        
        # Use threading primitives for safe state management
        self._stop_event = threading.Event()
        self._clicking_event = threading.Event()
        self._toggle_lock = threading.Lock()
        self.click_thread = None
        
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
        Uses events for clean shutdown and state management.
        """
        next_click_time = time.perf_counter()
        
        while not self._stop_event.is_set():
            current_time = time.perf_counter()
            
            # Only click if clicking is enabled
            if self._clicking_event.is_set():
                if current_time >= next_click_time:
                    self.mouse_controller.click(mouse.Button.left, 1)
                    next_click_time = current_time + self.click_interval
                
                # Sleep until next click time, but wake up periodically to check stop event
                sleep_time = max(0, min(next_click_time - current_time, 0.01))
                time.sleep(sleep_time)
            else:
                # Not clicking, just wait for state change
                time.sleep(0.01)

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
        """Toggle the clicking state with thread-safe locking"""
        with self._toggle_lock:
            if self._clicking_event.is_set():
                # Turning off
                self._clicking_event.clear()
                status = "stopped"
            else:
                # Turning on - create thread if needed
                self._clicking_event.set()
                if not self.click_thread or not self.click_thread.is_alive():
                    self.click_thread = threading.Thread(target=self.simulate_mouse_click)
                    self.click_thread.daemon = True
                    self.click_thread.start()
                status = "started"
        
        print(f"\rMouse clicking {status}     ", end="", flush=True)

    def on_release(self, key):
        """
        Handles key release events.
        """
        if key == keyboard.Key.esc:
            print("\nStopping auto clicker")
            self.request_stop()
            return False  # Stop listener
    
    def request_stop(self):
        """Request a clean shutdown of all components"""
        self._stop_event.set()
        self._clicking_event.clear()

    def cleanup(self):
        """Clean up resources before exiting"""
        self.request_stop()
        
        # Wait for click thread to terminate gracefully
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)
            if self.click_thread.is_alive():
                print("Warning: Click thread did not terminate cleanly")

    def start(self):
        """
        Starts the auto clicker with both keyboard and mouse listeners.
        Exception-safe: ensures listeners are properly stopped even if startup fails.
        """
        keyboard_listener = None
        mouse_listener = None

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
            
        finally:
            # Safely stop both listeners
            if mouse_listener is not None:
                mouse_listener.stop()
            if keyboard_listener is not None:
                keyboard_listener.stop()
            
            self.cleanup()
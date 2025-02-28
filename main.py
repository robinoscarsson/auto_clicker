from pynput import keyboard, mouse
import threading
import time

mouse_controller = mouse.Controller()

is_mouse_clicking = False

def simulate_mouse_click():
    """
    Simulates mouse clicks at regular intervals.

    This function runs in a loop, clicking the left mouse button every 10 milliseconds
    while the global flag `is_mouse_clicking` is set to True. The function is intended
    to be run in a separate thread and will stop clicking when `is_mouse_clicking` is
    set to False.
    """
    global is_mouse_clicking
    while is_mouse_clicking:
        mouse_controller.click(mouse.Button.left, 1)
        time.sleep(0.01)  # Sleep for 10 milliseconds

def on_press(key):
    """
    Handles key press events.

    This function is called whenever a key is pressed. If the F1 key is pressed,
    it toggles the `is_mouse_clicking` flag and starts or stops the mouse clicking
    simulation accordingly. If any other key is pressed, it logs the key press.

    Args:
        key: The key that was pressed.
    """
    global is_mouse_clicking
    try:
        if key == keyboard.Key.f1:
            is_mouse_clicking = not is_mouse_clicking
            if is_mouse_clicking:
                threading.Thread(target=simulate_mouse_click).start()
            print(f"Mouse clicking {'started' if is_mouse_clicking else 'stopped'}")
    except AttributeError:
        print(f"Special key pressed: {key}")

def on_release(key):
    """
    Handles key release events.

    This function is called whenever a key is released. If the Esc key is released,
    it stops the keyboard listener, effectively terminating the program.

    Args:
        key: The key that was released.
    """
    if key == keyboard.Key.esc:
        # Stop listener
        print("Stopping listener")
        return False

def main(*args, **kwargs):
    """
    Starts the autoclicker program.

    This function sets up and starts the keyboard listener. It prints instructions
    to the console and listens for key press and release events. Pressing the F1 key
    toggles the mouse clicking simulation on and off. Pressing the Esc key stops the
    listener and terminates the program.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    print("Starting autoclicker. Press F1 to start/stop clicking. Press ESC to exit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
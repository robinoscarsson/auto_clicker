from pynput import keyboard, mouse
import threading
import time

mouse_controller = mouse.Controller()

is_mouse_clicking = False

def simulate_mouse_click():
    global is_mouse_clicking
    while is_mouse_clicking:
        mouse_controller.click(mouse.Button.left, 1)
        time.sleep(0.01)  # Sleep for 10 milliseconds

def on_press(key):
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
    if key == keyboard.Key.esc:
        # Stop listener
        print("Stopping listener")
        return False

def main(*args, **kwargs):
    print("Starting autoclicker. Press F1 to start/stop clicking. Press ESC to exit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
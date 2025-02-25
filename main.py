from pynput import keyboard, mouse
import logging
import threading
import time

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

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
            logger.info(f"Mouse clicking {'started' if is_mouse_clicking else 'stopped'}")
    except AttributeError:
        logger.info(f"Special key pressed: {key}")

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        logger.info("Stopping listener")
        return False

def main(*args, **kwargs):
    logger.info("Starting autoclicker. Press F1 to start/stop clicking. Press ESC to exit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
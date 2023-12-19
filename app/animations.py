import time
from rpi_ws281x import Color
import random
import math
import colorsys
import matplotlib.colors as mcolors

fluctuating_color = [3, 30, 0]
tap_window = 1
tap_count = 0
last_tap_time = 0
mode = 1

# Threading animation pieces
#my_thread = None
#should_cont = True

#def stop_thread():
#    global should_cont, my_thread
#    should_cont = False
#    if my_thread is not None and my_thread.is_alive():
#        my_thread.join()
#        my_thread = None
#        print("INFO: Thread stopped")

def color_to_rgb(color):
    if color in mcolors.CSS4_COLORS:
        rgb_value = tuple(int(val * 255) for val in mcolors.to_rgb(mcolors.CSS4_COLORS[color]))
        return rgb_value
    
    else:
        raise ValueError("Color name not found in CSS4_COLORS")
            

def color_to_hex(color):
    hex_value = mcolors.to_hex(color)
    return hex_value


def tap_detected(channel):
    global tap_count, last_tap_time, mode
    current_time = time.time()
    
    if current_time - last_tap_time <= tap_window:
        tap_count += 1
    else:
        tap_count = 1
    
    last_tap_time = current_time

    print("Tap detected:", tap_count, flush=True)
    
    if tap_count == 4:
        print("Four taps detected in succession!")
        mode+=1
        if mode > 3:
            mode = 1
        print(f"Mode is: {mode}", flush=True)
        # Reset tap count
        tap_count = 0

# Define functions which animate LEDs in various ways.
def blink(strip, blinks=3):
    #Blink on/off
    cur_color = strip.getPixelColor(7)
    time.sleep(1)
    for j in range(blinks):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(1/4)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, cur_color)
        strip.show()
        time.sleep(1/4)

## COLOR SHADES
color_dict = {
    'blue': [
        (173, 216, 230), #lightblue
        (176, 224, 230), #powderblue
        (176, 196, 222), #lightsteelblue
        (135, 206, 250), #lightskyblue
        (135, 206, 235), #skyblue
        (0, 191, 255),   #deepskyblue
        (30, 144, 255),  #dodgerblue
        (70, 130, 180),  #steelblue
        (100, 149, 237), #cornflowerblue
        (65, 105, 225),  #royalblue
        (0, 0, 205),     #mediumblue
        (0, 0, 139),     #darkblue
        (0, 0, 128),     #navy
        (25, 25, 112),   #midnightblue
        (0, 0, 255),     #blue
        (72, 209, 204),  #mediumturquoise
        (64, 224, 208),  #turquoise
        (0, 206, 209),   #darkturquoise
        (127, 255, 212)  #aquamarine
    ],
    'purple': [
        (230, 230, 250),    # lavender
        (221, 160, 221),    # plum
        (218, 112, 214),    # orchid
        (186, 85, 211),     # mediumorchid
        (147, 112, 219),    # mediumpurple
        (138, 43, 226),     # blueviolet
        (128, 0, 128),      # purple
        (148, 0, 211),      # darkviolet
        (139, 0, 139),      # darkmagenta
        (153, 50, 204),     # darkorchid
        (102, 51, 153),     # rebeccapurple
        (123, 104, 238),    # mediumslateblue
    ],
    'yellow': [
        (255, 255, 224),  # lightyellow
        (255, 255, 204),  # lightgoldenrodyellow
        (255, 255, 153),  # lemonchiffon
        (255, 255, 102),  # lightgoldenrod
        (255, 255, 0),    # yellow
        (255, 215, 0),    # gold
        (238, 221, 130),  # moccasin
        (218, 165, 32),   # goldenrod
        (184, 134, 11),   # darkgoldenrod
        (139, 69, 19)     # saddlebrown (a darker shade for variety)
    ],
    'pink': [
        (255, 182, 193),  # lightpink
        (255, 192, 203),  # pink
        (219, 112, 147),  # palevioletred
        (255, 105, 180),  # hotpink
        (255, 20, 147),   # deepink
        (255, 0, 255),    # magenta
        (238, 130, 238),  # violet
    ],
    'red': [
        (205, 92, 92),      # indianred
        (220, 20, 60),       # crimson
        (178, 34, 34),       # firebrick
        (139, 0, 0),         # darkred
        (255, 0, 0),         # red
        (255, 99, 71),        # tomato
        (255, 69, 0),         # orangered
        (128, 0, 0),         # maroon
        (128, 0, 0),         # darkmaroon
        (255, 140, 0),       # darkorange
        (255, 165, 0),       # orange
    ],
    'green': [
        (240, 255, 240),      # honeydew
        (245, 255, 250),      # mintcream
        (46, 139, 87),        # seagreen
        (60, 179, 113),       # mediumseagreen
        (0, 255, 127),        # springgreen
        (152, 251, 152),      # palegreen
        (144, 238, 144),      # lightgreen
        (102, 205, 170),      # mediumaquamarine
        (127, 255, 212),      # aquamarine
        (0, 250, 154),        # mediumspringgreen
        (127, 255, 0),        # chartreuse
        (124, 252, 0),        # lawngreen
        (0, 255, 0),          # lime
        (50, 205, 50),        # limegreen
        (173, 255, 47),       # greenyellow
        (85, 107, 47),        # darkolivegreen
        (107, 142, 35),       # olivedrab
        (128, 128, 0),        # olive
        (0, 128, 0),          # green
        (0, 100, 0),          # darkgreen
        (34, 139, 34),        # forestgreen
        (143, 188, 143)       # darkseagreen
    ],
}

def get_hues_of_color(base_color):
    for key, values in color_dict.items():
        if base_color in values:
            return values

    return None


def flux(start_color, end_color):

    global fluctuating_color
    fluctuating_color = [0, 0, 0]

    # Define the total number of steps for the fluctuation
    total_steps = 4 # Adjust this value to control the speed of change

    # Calculate the step size for each color channel
    step_size = tuple((end - start) / total_steps for start, end in zip(start_color, end_color))

    # Generate the fluctuating colors
    for i in range(total_steps):
        red_value = start_color[0] + int(step_size[0] * i)
        green_value = start_color[1] + int(step_size[1] * i)
        blue_value = start_color[2] + int(step_size[2] * i)
        fluctuating_color = [red_value, green_value, blue_value]
        yield fluctuating_color

    # Reverse the process to generate the colors back to the starting point
    for i in range(total_steps, 0, -1):
        red_value = start_color[0] + int(step_size[0] * i)
        green_value = start_color[1] + int(step_size[1] * i)
        blue_value = start_color[2] + int(step_size[2] * i)
        fluctuating_color = [red_value, green_value, blue_value]
        yield fluctuating_color


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def colorWipeReverse(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()-1,-1,-1):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

    """
#def theaterChase(strip, color, wait_ms=50, iterations=10):
#def theaterChase(strip, color, wait_ms=50):
    #Movie theater light style chaser animation.
    global should_cont
    should_cont = True
    while should_cont:
    # for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)
"""

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


'''
def rainbow(strip, wait_ms=20):
    """Draw rainbow that fades across all pixels at once."""
    #for j in range(256 * iterations):
   # global should_cont
   # should_cont = True
   # while should_cont:
        for j in range(256):
            #if not should_cont:
                break
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
'''

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    global mode
    while mode == 3:
        for j in range(256):
            for i in range(strip.numPixels()):
                if mode != 3:
                    break
                strip.setPixelColor(i, wheel(
                    (int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)

def print_colored_block(r, g, b):  #Used for printing to terminal for testing
    # ANSI escape codes for color
    color_code = f"\033[38;2;{r};{g};{b}m"
    reset_code = "\033[0m"

    # ASCII character 219 (block) and color codes
    colored_block = f"{color_code}█{reset_code}"

    print(colored_block)

"""
def theaterChaseRainbow(strip, wait_ms=50):
    #Rainbow movie theater light style chaser animation.
    global should_cont
    should_cont = True
    while should_cont:
        for j in range(256):
            if not should_cont:
                break
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, wheel((i + j) % 255))
                strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, 0)

def fire(strip, cooling=55, sparking=120, delay=15):
    cooldown = 0
    heat = [0] * strip.numPixels()

    #Cool down
    for i in range(strip.numPixels()):
        cooldown = random.randint(0, ((cooling * 10) / strip.numPixels()) + 2)
        if cooldown > heat[i]:
            heat[i]=0
        else:
            heat[i]=heat[i]-cooldown

    #Heat drift
    for m in range(strip.numPixels()-1, 2, -1):
        heat[m] = (heat[m-1] + heat[m - 2] + heat[m - 2]) / 3

    #Ignite random sparks
    if random.randint(0, 255) < sparking:
        x = random.randint(0, 255)
        heat[x] = heat[x] + random.randint(160, 255)

    #Convert heat to LED color
    for i in range(strip.numPixels()):
        #setHeatColor(i, heat[i])
        print("Convert: i is: '{}' and heat i is: {}".format(i, heat[i]))
        #input("Press Enter to continue...")

    strip.show()
    time.sleep(delay)     

#def setHeatColor(pixel, temp)   

def running(strip, red, green, blue, delay):
    pos = 0
    global should_cont
    should_cont = True
    while should_cont:
        pos+=1

# Define colors
#deep_blue = Color(0, 0, 255)
#light_blue = Color(135, 206, 250)

def breath(strip, wait_ms=20):
    #Draw a breathing color across all pixels.
    global should_cont
    should_cont = True
    while should_cont:
        #strip.setBrightness(x)
        for i in range(strip.numPixels()):
            r = random.randint(0, 135)
            g = random.randint(0, 206)
            b = random.randint(250, 255)
            strip.setPixelColorRGB(i, r, g, b)
        strip.show()
        time.sleep(wait_ms / 100.0)

def breathSlide(strip, min_r=0, max_r=100, min_g=0, max_g=206, min_b=240, max_b=255, min_brightness=1, max_brightness=40, wait_ms=10):
    while True:
        for b in range(0, 720):
             # Calculate the brightness value based on a sine wave
            brightness = int(math.sin(math.radians(b*4.5)) * (max_brightness - min_brightness) / 2 + (max_brightness + min_brightness) / 2)
            
            # Set the LED brightness
            strip.setBrightness(brightness)

            # Set the color of the first LED to a random color within the specified RGB range
            color = Color(random.randint(min_r, max_r), random.randint(min_g, max_g), random.randint(min_b, max_b))
            strip.setPixelColor(0, color)

            # Loop through all the other LEDs and set their color to the color of the previous LED
            for i in range(strip.numPixels() - 1, 0, -1):
                prev_color = strip.getPixelColor(i-1)
                strip.setPixelColor(i, prev_color)
                
            # Display the updated LED colors
            strip.show()
            time.sleep(wait_ms / 100.0)

def breathSlide(strip, wait_ms=20):
    #Draw a breathing color across all pixels.
    global should_cont
    should_cont = True
    while should_cont:
        for i in range(strip.numPixels()):
            r = random.randint(0, 135)
            g = random.randint(0, 206)
            b = random.randint(250, 255)
            strip.setPixelColorRGB(i, r, g, b)
        strip.show()
        time.sleep(wait_ms / 100.0)

    
    global should_cont
    should_cont = True
    while should_cont:
        for j in range(256):
            if not should_cont:
                break
            elif j < 128:
                # Color is getting deeper
                color = struct.unpack('i', struct.pack('I', Color(0, int(2.0 * j), int(5.0 * j), int(10.0 * j))))[0]
            else:
                # Color is getting lighter
                color = struct.unpack('i', struct.pack('I', Color(int(2.0 * (255 - j)), int(5.0 * (255 - j)), int(10.0 * (255 - j)))))[0]
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
    
    

def breathing(strip, frequency, min_brightness, max_brightness):
    while True:
        for i in range(0, 360):
            # Calculate the brightness value based on a sine wave
            brightness = int(math.sin(math.radians(i)) * (max_brightness - min_brightness) / 2 + (max_brightness + min_brightness) / 2)
            
            # Set the LED brightness
            #led.duty(brightness)
            
            # Pause for a short time to create the breathing effect
            time.sleep(frequency / 700)
            print(brightness)         
"""


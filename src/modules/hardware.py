import board
import digitalio
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7789 as st7789
import adafruit_rgb_display.ili9341 as ili9341
import yaml
import os

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.yaml')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("Warning: Config not found, using defaults")
    config = {}

class HardwareManager:
    def __init__(self):
        self.disp = None
        self.width = 240
        self.height = 240
        self.setup_display()
        self.setup_buttons()

    def setup_display(self):
        """Initialize the SPI display based on config"""
        # Configuration for CS and DC pins (these are PiTFT defaults):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D27)

        # Config for display baudrate (speed)
        BAUDRATE = 64000000

        # Setup SPI bus using hardware SPI:
        spi = board.SPI()

        # Check display mode
        display_mode = config.get('system', {}).get('display_mode', 'tft')
        
        if display_mode == 'window':
            print("Running in WINDOW mode (VNC/HDMI). SPI Display disabled.")
            self.disp = None
            return

        # Initialize display (defaulting to ST7789, typical for 1.3" - 2.0" screens)
        # For larger 2.8"+ screens, ILI9341 is common.
        # We can make this configurable.
        try:
            self.disp = st7789.ST7789(
                spi,
                cs=cs_pin,
                dc=dc_pin,
                rst=reset_pin,
                baudrate=BAUDRATE,
                width=240,
                height=240,
                x_offset=0,
                y_offset=0,
            )
            # Turn on backlight (some screens need this)
            self.backlight = digitalio.DigitalInOut(board.D22)
            self.backlight.switch_to_output()
            self.backlight.value = True
        except Exception as e:
            print(f"Hardware Display Init Failed (Running in Headless/Mock Mode?): {e}")
            self.disp = None

        if self.disp:
            self.width = self.disp.width
            self.height = self.disp.height

    def setup_buttons(self):
        """Setup GPIO buttons"""
        # Example button setup
        self.button_a = digitalio.DigitalInOut(board.D23)
        self.button_a.direction = digitalio.Direction.INPUT
        self.button_a.pull = digitalio.Pull.UP

        self.button_b = digitalio.DigitalInOut(board.D24)
        self.button_b.direction = digitalio.Direction.INPUT
        self.button_b.pull = digitalio.Pull.UP

    def update_display(self, image):
        """
        Update the display with a PIL Image.
        Args:
            image (PIL.Image): Image to display. Must match screen dimensions.
        """
        if self.disp:
            self.disp.image(image)

    def check_buttons(self):
        """Return button states"""
        # Logic is inverted for Pull.UP (False when pressed)
        return {
            "A": not self.button_a.value,
            "B": not self.button_b.value
        }

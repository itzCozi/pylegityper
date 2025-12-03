import ctypes
import random
import shutil
import time
from ctypes import wintypes
from typing import Any, Literal, Self, Tuple

import win32api
from win32con import *


class CancelRequested(Exception):
  """Raised when the Ctrl+Alt cancel hotkey is detected."""


CTRL_VKS: tuple[int, ...] = (VK_CONTROL, VK_LCONTROL, VK_RCONTROL)
ALT_VKS: tuple[int, ...] = (VK_MENU, VK_LMENU, VK_RMENU)


def _is_pressed(vk_codes: tuple[int, ...]) -> bool:
  return any(win32api.GetAsyncKeyState(code) & 0x8000 for code in vk_codes)


def cancel_hotkey_pressed() -> bool:
  return _is_pressed(CTRL_VKS) and _is_pressed(ALT_VKS)


def sleep_with_cancel(duration: float, poll_interval: float = 0.05) -> None:
  """Sleep in small chunks while watching for the cancel hotkey."""
  end_time: float = time.monotonic() + max(0.0, duration)
  while True:
    if cancel_hotkey_pressed():
      raise CancelRequested
    remaining: float = end_time - time.monotonic()
    if remaining <= 0:
      break
    time.sleep(min(poll_interval, remaining))


class Keyboard:
  @staticmethod
  def error(
      error_type: str,
      var: str = None,
      type: str = None,
      runtime_error: str = None
  ) -> None:
    """
    Display error messages based on the type of error encountered.
    """
    if error_type == "p":
      print(f"PARAMETER - Given variable {var} is not a {type}.")
    elif error_type == "r":
      print(f"RUNTIME - {runtime_error.capitalize()}.")
    elif error_type == "u":
      print("UNKNOWN - An unknown error was encountered.")
    return None

  exit_code: None = None  # Exit code for error handling
  INPUT_MOUSE: int = 0
  WM_KEYUP: int = 0x0101
  INPUT_KEYBOARD: int = 1
  WH_KEYBOARD_LL: int = 13
  MAPVK_VK_TO_VSC: int = 0
  WM_KEYDOWN: int = 0x0100
  KEYEVENTF_KEYUP: int = 0x0002
  KEYEVENTF_UNICODE: int = 0x0004
  KEYEVENTF_SCANCODE: int = 0x0008
  KEYEVENTF_EXTENDEDKEY: int = 0x0001
  user32: ctypes.WinDLL = ctypes.WinDLL("user32", use_last_error=True)

  # Reference: https://msdn.microsoft.com/en-us/library/dd375731
  # Each key value is 4 chars long and formatted in hexadecimal
  vk_codes: dict = {
    # --------- Mouse ---------
    "left_mouse": 0x01,
    "right_mouse": 0x02,
    "middle_mouse": 0x04,
    "mouse_button1": 0x05,
    "mouse_button2": 0x06,
    # ----- Control Keys ------
    "win": 0x5B,  # Left Windows key
    "select": 0x29,
    "pg_down": 0x21,
    "pg_up": 0x22,
    "end": 0x23,
    "home": 0x24,
    "insert": 0x2D,
    "delete": 0x2E,
    "back": 0x08,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "caps": 0x14,
    "escape": 0x1B,
    "space": 0x20,
    "tab": 0x09,
    "sleep": 0x5F,
    "zoom": 0xFB,
    "num_lock": 0x90,
    "scroll_lock": 0x91,
    # ----- OEM Specific ------
    "plus": 0xBB,
    "comma": 0xBC,
    "minus": 0xBD,
    "period": 0xBE,
    # -------- Media ----------
    "vol_mute": 0xAD,
    "vol_down": 0xAE,
    "vol_up": 0xAF,
    "next": 0xB0,
    "prev": 0xB1,
    "stop": 0xB2,
    "pause_play": 0xB3,
    # ------ Arrow Keys -------
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    # ----- Function Keys -----
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B,
    "f13": 0x7C,
    "f14": 0x7D,
    "f15": 0x7E,
    "f16": 0x7F,
    "f17": 0x80,
    "f18": 0x81,
    "f19": 0x82,
    "f20": 0x83,
    "f21": 0x84,
    "f22": 0x85,
    "f23": 0x86,
    "f24": 0x87,
    # -------- Keypad ---------
    "pad_0": 0x60,
    "pad_1": 0x61,
    "pad_2": 0x62,
    "pad_3": 0x63,
    "pad_4": 0x64,
    "pad_5": 0x65,
    "pad_6": 0x66,
    "pad_7": 0x67,
    "pad_8": 0x68,
    "pad_9": 0x69,
    # -------- Symbols --------
    "multiply": 0x6A,
    "add": 0x6B,
    "separator": 0x6C,
    "subtract": 0x6D,
    "decimal": 0x6E,
    "divide": 0x6F,
    # ---- Alphanumerical -----
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "a": 0x41,
    "b": 0x42,
    "c": 0x43,
    "d": 0x44,
    "e": 0x45,
    "f": 0x46,
    "g": 0x47,
    "h": 0x48,
    "i": 0x49,
    "j": 0x4A,
    "k": 0x4B,
    "l": 0x4C,
    "m": 0x4D,
    "n": 0x4E,
    "o": 0x4F,
    "p": 0x50,
    "q": 0x51,
    "r": 0x52,
    "s": 0x53,
    "t": 0x54,
    "u": 0x55,
    "v": 0x56,
    "w": 0x57,
    "x": 0x58,
    "y": 0x59,
    "z": 0x5A,
    "=": 0x6B,
    " ": 0x20,
    ".": 0xBE,
    ",": 0xBC,
    "-": 0x6D,
    "`": 0xC0,
    "/": 0xBF,
    ";": 0xBA,
    "[": 0xDB,
    "]": 0xDD,
    "_": 0x6D,   # Shift
    "|": 0xDC,   # Shift
    "~": 0xC0,   # Shift
    "?": 0xBF,   # Shift
    ":": 0xBA,   # Shift
    "<": 0xBC,   # Shift
    ">": 0xBE,   # Shift
    "{": 0xDB,   # Shift
    "}": 0xDD,   # Shift
    "!": 0x31,   # Shift
    "@": 0x32,   # Shift
    "#": 0x33,   # Shift
    "$": 0x34,   # Shift
    "%": 0x35,   # Shift
    "^": 0x36,   # Shift
    "&": 0x37,   # Shift
    "*": 0x38,   # Shift
    "(": 0x39,   # Shift
    ")": 0x30,   # Shift
    "+": 0x6B,   # Shift
    "\"": 0xDE,  # Shift
    "\'": 0xDE,
    "\\": 0xDC,
    "\n": 0x0D
  }

  # C struct declarations, recently added type hinting
  wintypes.ULONG_PTR: type[wintypes.WPARAM] = wintypes.WPARAM  # type: ignore
  global MOUSEINPUT, KEYBDINPUT

  class MOUSEINPUT(ctypes.Structure):
    _fields_: tuple[
      tuple[Literal["dx"], wintypes.LONG],                  # A
      tuple[Literal["dy"], wintypes.LONG],                  # B
      tuple[Literal["mouseData"], wintypes.DWORD],          # C
      tuple[Literal["dwFlags"], wintypes.DWORD],            # D
      tuple[Literal["time"], wintypes.DWORD],               # E
      tuple[Literal["dwExtraInfo"], type[wintypes.WPARAM]]  # F
    ] = (
      ("dx", wintypes.LONG),                                # A
      ("dy", wintypes.LONG),                                # B
      ("mouseData", wintypes.DWORD),                        # C
      ("dwFlags", wintypes.DWORD),                          # D
      ("time", wintypes.DWORD),                             # E
      ("dwExtraInfo", wintypes.ULONG_PTR)                   # F
    )

  class KEYBDINPUT(ctypes.Structure):
    _fields_: tuple[
      tuple[Literal["wVk"], wintypes.WORD],                 # A
      tuple[Literal["wScan"], wintypes.WORD],               # B
      tuple[Literal["dwFlags"], wintypes.DWORD],            # C
      tuple[Literal["time"], wintypes.DWORD],               # D
      tuple[Literal["dwExtraInfo"], type[wintypes.WPARAM]]  # E
    ] = (
      ("wVk", wintypes.WORD),                               # A
      ("wScan", wintypes.WORD),                             # B
      ("dwFlags", wintypes.DWORD),                          # C
      ("time", wintypes.DWORD),                             # D
      ("dwExtraInfo", wintypes.ULONG_PTR)                   # E
    )

    def __init__(
        this: Self,
        *args: tuple[Any, ...],
        **kwds: dict[str, Any]
    ) -> None:
      # *args & **kwds are confusing asf: https://youtu.be/4jBJhCaNrWU
      super(KEYBDINPUT, this).__init__(*args, **kwds)
      if not this.dwFlags & Keyboard.KEYEVENTF_UNICODE:
        this.wScan: Any = Keyboard.user32.MapVirtualKeyExW(
          this.wVk, Keyboard.MAPVK_VK_TO_VSC, 0
        )

  class INPUT(ctypes.Structure):

    class _INPUT(ctypes.Union):
      _fields_: tuple[
        tuple[Literal["ki"], type[KEYBDINPUT]],
        tuple[Literal["mi"], type[MOUSEINPUT]]
      ] = (("ki", KEYBDINPUT), ("mi", MOUSEINPUT))

    _anonymous_: tuple[Literal["_input"]] = ("_input",)
    _fields_: tuple[
      tuple[Literal["type"], wintypes.DWORD],
      tuple[Literal["_input"], type[_INPUT]]
    ] = (("type", wintypes.DWORD), ("_input", _INPUT))

  LPINPUT: Any = ctypes.POINTER(INPUT)

  # Helpers / Bare-bones implementation

  @staticmethod
  def _checkCount(result: Any, func: Any, args: Any) -> Any:
    if result == 0:
      raise ctypes.WinError(ctypes.get_last_error())
    return args

  @staticmethod
  def _lookup(key: Any) -> int | bool:
    if key in Keyboard.vk_codes:
      return Keyboard.vk_codes.get(key)
    else:
      return False

  @staticmethod
  def mouseScroll(axis: str, dist: int, x: int = 0, y: int = 0) -> None | bool:
    if axis == "v" or axis == "vertical":
      win32api.mouse_event(MOUSEEVENTF_WHEEL, x, y, dist, 0)  # noqa: F405 MOUSEEVENTF_WHEEL is a windows thing
    elif axis == "h" or axis == "horizontal":
      win32api.mouse_event(MOUSEEVENTF_HWHEEL, x, y, dist,
                           0)  # noqa: F405 MOUSEEVENTF_HWHEEL is a windows thing as well
    else:
      return False

  class ManipulateMouse:
    """
    A simple class to control the mouse cursor

    Functions:
      getPosition(): Returns a tuple with the cursor's current position
      setPosition(x, y): Moves the cursor to the given x and y coordinates
    """

    @staticmethod
    def getPosition() -> tuple:
      """
      Retrieve the current position of the mouse cursor.
      """

      # Define the POINT structure to store cursor position
      class POINT(ctypes.Structure):
        _fields_: list = [("x", ctypes.c_long), ("y", ctypes.c_long)]

      point: POINT = POINT()
      ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
      return (point.x, point.y)

    @staticmethod
    def setPosition(x: int, y: int) -> None:
      """
      Set the position of the mouse cursor to the given coordinates.
      """
      ctypes.windll.user32.SetCursorPos(x, y)

  # Type annotation not supported
  user32.SendInput.errcheck = _checkCount
  user32.SendInput.argtypes = (
    wintypes.UINT,  # nInputs
    LPINPUT,        # pInputs
    ctypes.c_int    # cbSize
  )

  # Functions (most people will only use these)

  @staticmethod
  def getKeyState(key_code: str | int) -> bool:
    """
    Returns the given key's current state

    Args:
      key_code (str | int): The key to be checked for state

    Returns:
      bool: "False" if the key is not pressed and "True" if it is
    """
    if not isinstance(key_code, str | int):
      Keyboard.error(error_type="p", var="key_code",
                     type="integer or string")
      return Keyboard.exit_code

    if Keyboard._lookup(key_code) is not False:
      key_code: int = Keyboard._lookup(key_code)
    elif key_code not in Keyboard.vk_codes and key_code not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    integer_state: int = Keyboard.user32.GetKeyState(key_code)
    key_state: bool = True if integer_state == 1 else False

    if "key_state" in locals():
      return key_state
    else:
      Keyboard.error(
        error_type="r", runtime_error="user32 returned a non \"1\" or \"0\" value"
      )
      return Keyboard.exit_code

  @staticmethod
  def locateCursor() -> Tuple[int, int]:
    """
    Returns a tuple of the current X & Y coordinates of the mouse

    Returns:
      tuple[int, int]: The current X and Y coordinates EX: (350, 940)
    """

    # The ManipulateMouse class has a function for this
    return Keyboard.ManipulateMouse.getPosition()

  @staticmethod
  def moveCursor(x: int, y: int) -> None:
    """
    Moves the cursor to a specific coordinate on the screen.

    Args:
      x (int): The x-coordinate to be sent to user32
      y (int): The y-coordinate to be sent to user32
    """
    if not isinstance(x, int):
      Keyboard.error(error_type="p", var="x", type="integer")
      return Keyboard.exit_code
    if not isinstance(y, int):
      Keyboard.error(error_type="p", var="y", type="integer")
      return Keyboard.exit_code

    # The ManipulateMouse class also has a function for this
    Keyboard.ManipulateMouse.setPosition(x, y)

  @staticmethod
  def scrollMouse(direction: str, amount: int, dx: int = 0, dy: int = 0) -> None:
    """
    Scrolls mouse up, down, right and left by a certain amount

    Args:
      direction (str): The way to scroll, valid inputs: (
        up, down, right, left
      )
      amount (int): How much to scroll has to be at least 1
      dx (int, optional): The mouse's position on the x-axis
      dy (int, optional): The mouse's position on the y-axis
    """
    if not isinstance(direction, str):
      Keyboard.error(error_type="p", var="direction", type="string")
      return Keyboard.exit_code
    if not isinstance(amount, int):
      Keyboard.error(error_type="p", var="amount", type="integer")
      return Keyboard.exit_code
    if not isinstance(dx, int):
      Keyboard.error(error_type="p", var="dx", type="integer")
      return Keyboard.exit_code
    if not isinstance(dy, int):
      Keyboard.error(error_type="p", var="dy", type="integer")
      return Keyboard.exit_code

    direction_list: list = ["up", "down", "left", "right"]
    if direction not in direction_list:
      Keyboard.error(
        error_type="r", runtime_error="given direction is not valid")
      return Keyboard.exit_code
    if amount < 1:
      Keyboard.error(
        error_type="r", runtime_error="given amount is less than 1")
      return Keyboard.exit_code

    if direction == "up":
      Keyboard.mouseScroll("vertical", amount, dx, dy)
    elif direction == "down":
      Keyboard.mouseScroll("vertical", -amount, dx, dy)
    elif direction == "right":
      Keyboard.mouseScroll("horizontal", amount, dx, dy)
    elif direction == "left":
      Keyboard.mouseScroll("horizontal", -amount, dx, dy)

  @staticmethod
  def pressMouse(mouse_button: str | int) -> None:
    """
    Presses a mouse button

    Args:
      mouse_button (str | int): The button to press accepted: (
        left_mouse,
        right_mouse,
        middle_mouse,
        mouse_button1,
        mouse_button
      )
    """
    if not isinstance(mouse_button, str | int):
      Keyboard.error(
        error_type="p", var="mouse_button", type="integer or string")
      return Keyboard.exit_code

    mouse_list: list = [
      "left_mouse", 0x01, "right_mouse", 0x02, "middle_mouse", 0x04,
      "mouse_button1", 0x05, "mouse_button2", 0x06
    ]
    if mouse_button not in mouse_list and hex(mouse_button) not in mouse_list:
      Keyboard.error(
        error_type="r", runtime_error="given key code is not a mouse button")
      return Keyboard.exit_code

    if Keyboard._lookup(mouse_button) is not False:
      mouse_button: int = Keyboard._lookup(mouse_button)
    elif mouse_button not in Keyboard.vk_codes and mouse_button not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    x: Keyboard.INPUT = Keyboard.INPUT(
      type=Keyboard.INPUT_MOUSE,
      mi=MOUSEINPUT(
        wVk=mouse_button,
        dwFlags=Keyboard.KEYEVENTF_KEYUP
      )
    )
    Keyboard.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

  @staticmethod
  def releaseMouse(mouse_button: str | int) -> None:
    """
    Releases a mouse button

    Args:
      mouse_button (str | int): The button to press accepted: (
        left_mouse,
        right_mouse,
        middle_mouse,
        mouse_button1,
        mouse_button
      )
    """
    if not isinstance(mouse_button, str | int):
      Keyboard.error(
        error_type="p", var="mouse_button", type="integer or string")
      return Keyboard.exit_code

    mouse_list: list = [
      "left_mouse", 0x01, "right_mouse", 0x02, "middle_mouse", 0x04,
      "mouse_button1", 0x05, "mouse_button2", 0x06
    ]
    if mouse_button not in mouse_list and hex(mouse_button) not in mouse_list:
      Keyboard.error(
        error_type="r", runtime_error="given key code is not a mouse button"
      )
      return Keyboard.exit_code

    if Keyboard._lookup(mouse_button) is not False:
      mouse_button: int = Keyboard._lookup(mouse_button)
    elif mouse_button not in Keyboard.vk_codes and mouse_button not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    x: Keyboard.INPUT = Keyboard.INPUT(
      type=Keyboard.INPUT_MOUSE,
      mi=MOUSEINPUT(wVk=mouse_button)
    )
    Keyboard.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

  @staticmethod
  def pressKey(key_code: str | int) -> None:
    """
    Presses a keyboard key

    Args:
      key_code (str | int): All keys in vk_codes dict are valid
    """
    if not isinstance(key_code, str | int):
      Keyboard.error(error_type="p", var="key_code",
                     type="integer or string")
      return Keyboard.exit_code

    if Keyboard._lookup(key_code) is not False:
      key_code: int = Keyboard._lookup(key_code)
    elif key_code not in Keyboard.vk_codes and key_code not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    x: Keyboard.INPUT = Keyboard.INPUT(
      type=Keyboard.INPUT_KEYBOARD,
      ki=KEYBDINPUT(wVk=key_code)
    )
    Keyboard.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

  @staticmethod
  def releaseKey(key_code: str | int) -> None:
    """
    Releases a keyboard key

    Args:
      key_code (str | int): All keys in vk_codes dict are valid
    """
    if not isinstance(key_code, str | int):
      Keyboard.error(error_type="p", var="key_code",
                     type="integer or string")
      return Keyboard.exit_code

    if Keyboard._lookup(key_code) is not False:
      key_code: int = Keyboard._lookup(key_code)
    elif key_code not in Keyboard.vk_codes and key_code not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    x: Keyboard.INPUT = Keyboard.INPUT(
      type=Keyboard.INPUT_KEYBOARD,
      ki=KEYBDINPUT(
        wVk=key_code,
        dwFlags=Keyboard.KEYEVENTF_KEYUP
      )
    )
    Keyboard.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

  @staticmethod
  def pressAndReleaseKey(key_code: str | int) -> None:
    """
    Presses and releases a keyboard key sequentially

    Args:
      key_code (str | int): All keys in vk_codes dict are valid
    """
    if not isinstance(key_code, str | int):
      Keyboard.error(error_type="p", var="key_code",
                     type="integer or string")
      return Keyboard.exit_code

    if Keyboard._lookup(key_code) is not False:
      key_code: int = Keyboard._lookup(key_code)
    elif key_code not in Keyboard.vk_codes and key_code not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    Keyboard.pressKey(key_code)
    Keyboard.releaseKey(key_code)

  @staticmethod
  def pressAndReleaseMouse(mouse_button: str | int) -> None:
    """
    Presses and releases a mouse button sequentially

    Args:
      mouse_button (str | int): The button to press accepted: (
        left_mouse,
        right_mouse,
        middle_mouse,
        mouse_button1,
        mouse_button2
      )
    """
    if not isinstance(mouse_button, str | int):
      Keyboard.error(
        error_type="p", var="mouse_button", type="integer or string")
      return Keyboard.exit_code

    mouse_dict: dict[str, int] = {
      "left_mouse": 0x01,
      "right_mouse": 0x02,
      "middle_mouse": 0x04,
      "mouse_button1": 0x05,
      "mouse_button2": 0x06
    }

    if isinstance(mouse_button, str):
      if mouse_button not in mouse_dict:
        Keyboard.error(
          error_type="r", runtime_error="given key code is not a mouse button")
        return Keyboard.exit_code
      mouse_button_code: int = mouse_dict[mouse_button]
    else:
      if mouse_button not in mouse_dict.values():
        Keyboard.error(
          error_type="r", runtime_error="given key code is not a mouse button")
        return Keyboard.exit_code
      mouse_button_code: int = mouse_button

    original_name: str = mouse_button if isinstance(mouse_button, str) else next(
      key for key, value in mouse_dict.items() if value == mouse_button)

    if Keyboard._lookup(mouse_button_code) is not False:
      mouse_button_code: int | bool = Keyboard._lookup(mouse_button_code)
    elif mouse_button_code not in Keyboard.vk_codes and mouse_button_code not in Keyboard.vk_codes.values():
      Keyboard.error(
        error_type="r", runtime_error="given key code is not valid")
      return Keyboard.exit_code

    Keyboard.pressMouse(original_name)
    Keyboard.releaseMouse(original_name)

  @staticmethod
  def keyboardWrite(source_str: str) -> None:
    """
    Writes by sending virtual inputs

    Args:
      source_str (str): The string to be inputted on the keyboard, all
      keys in the "Alphanumerical" section of vk_codes dict are valid
    """
    if not isinstance(source_str, str):
      Keyboard.error(error_type="p", var="string", type="string")
      return Keyboard.exit_code

    shift_alternate: set[str] = set("|~?:{}\"!@#$%^&*()_+<>")
    for char in source_str:
      if char not in Keyboard.vk_codes and not char.isupper():
        Keyboard.error(
          error_type="r",
          runtime_error=f"character: {char} is not in vk_codes map"
        )
        return Keyboard.exit_code

      if char.isupper() or char in shift_alternate:
        Keyboard.pressKey("shift")
      else:
        Keyboard.releaseKey("shift")

      key_code: int | bool = Keyboard._lookup(char.lower())
      if key_code is False:
        Keyboard.error(
          error_type="r",
          runtime_error=f"character: {char} is not in vk_codes map"
        )
        return Keyboard.exit_code

      for flag in [0, Keyboard.KEYEVENTF_KEYUP]:
        x: Keyboard.INPUT = Keyboard.INPUT(
          type=Keyboard.INPUT_KEYBOARD,
          ki=KEYBDINPUT(wVk=key_code, dwFlags=flag)
        )
        Keyboard.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    Keyboard.releaseKey("shift")  # Ensure shift is released


class Typer:
  @staticmethod
  def legitTyper(string: str, wpm: int) -> None:
    """
    Simulates human-like typing by introducing random delays and mistakes.

    Args:
      string (str): The string to be typed out.
      wpm (int): The desired typing speed in words per minute.
    """
    if not isinstance(string, str):
      Keyboard.error(error_type="p", var="string", type="string")
      return Keyboard.exit_code
    if not isinstance(wpm, int):
      Keyboard.error(error_type="p", var="wpm", type="integer")
      return Keyboard.exit_code
    if wpm <= 0:
      Keyboard.error( 
        error_type="r", runtime_error="wpm must be a positive integer")
      return Keyboard.exit_code

    message_shown = False
    print("\rPress Alt + Ctrl to stop typing...", end="", flush=True)
    message_shown = True
    try:
      base_delay: float = 60.0 / (wpm * 5.0)

      def ensure_not_cancelled() -> None:
        if cancel_hotkey_pressed():
          raise CancelRequested

      def delay(mult: float = 1.0) -> None:
        ensure_not_cancelled()
        mean = base_delay * mult
        std = max(0.015, mean * 0.35)
        d = random.gauss(mean, std)
        d = max(0.02, min(d, base_delay * 3.0))
        sleep_with_cancel(d)

      def type_char(ch: str) -> None:
        ensure_not_cancelled()
        Keyboard.keyboardWrite(ch)

      def backspace(n: int = 1) -> None:
        for _ in range(n):
          ensure_not_cancelled()
          Keyboard.pressAndReleaseKey("back")
          sleep_with_cancel(0.02 + random.random() * 0.05)

      def supported(ch: str) -> bool:
        return (
          ch in Keyboard.vk_codes
          or ch.lower() in Keyboard.vk_codes
          or ch.isupper()
        )

      def neighbor_map() -> dict[str, list[str]]:
        rows = [
          "`1234567890-=",
          "qwertyuiop[]\\",
          "asdfghjkl;'",
          "zxcvbnm,./",
        ]
        rows = [r.lower() for r in rows]
        vk = Keyboard.vk_codes
        mapping: dict[str, list[str]] = {}
        for r_idx, row in enumerate(rows):
          for c_idx, ch in enumerate(row):
            neigh: set[str] = set()
            for dc in (-1, 1):
              cc = c_idx + dc
              if 0 <= cc < len(row):
                neigh.add(row[cc])
            for dr in (-1, 1):
              rr = r_idx + dr
              if 0 <= rr < len(rows):
                other = rows[rr]
                for dc in (-1, 0, 1):
                  cc = c_idx + dc
                  if 0 <= cc < len(other):
                    neigh.add(other[cc])
            mapping[ch] = [n for n in neigh if (n in vk)]
        return mapping

      NEIGHBORS = neighbor_map()

      # Higher-level cadence knobs
      mistake_prob_neighbor = 0.06     # hit adjacent wrong key and fix
      mistake_prob_double = 0.03       # double press a key then backspace
      mistake_prob_transpose = 0.02    # hit the next char first, then backspace
      pause_after_space_chance = 0.18  # occasional thinking pause after spaces

      i = 0
      while i < len(string):
        ensure_not_cancelled()
        ch = string[i]

        if not supported(ch):
          i += 1
          continue

        if ch in ".!?":
          punct_mult = 5.0
        elif ch in ",;:":
          punct_mult = 2.5
        elif ch == " ":
          punct_mult = 1.4
        else:
          punct_mult = 1.0

        r = random.random()
        made_mistake = False

        if (
          r < mistake_prob_transpose
          and i + 1 < len(string)
          and string[i + 1] != "\n"
          and supported(string[i + 1])
        ):
          wrong = string[i + 1]
          type_char(wrong)
          delay(0.6)
          backspace()
          made_mistake = True

        elif r < mistake_prob_transpose + mistake_prob_neighbor:
          neighs = NEIGHBORS.get(ch.lower(), [])
          if neighs:
            wrong = random.choice(neighs)
            wrong = wrong.upper() if ch.isupper() else wrong
            type_char(wrong)
            delay(0.75)
            backspace()
            made_mistake = True

        elif r < mistake_prob_transpose + mistake_prob_neighbor + mistake_prob_double:
          type_char(ch)
          delay(0.45)
          type_char(ch)
          delay(0.6)
          backspace()
          delay(punct_mult)
          i += 1
          continue

        type_char(ch)

        delay(punct_mult * (1.1 if made_mistake else 1.0))

        if ch == " " and random.random() < pause_after_space_chance:
          sleep_with_cancel(random.uniform(0.15, 0.65) + base_delay * random.uniform(1.5, 3.5))

        i += 1
    finally:
      if message_shown:
        clear_status_line()


def clear_status_line() -> None:
  try:
    cols: int = shutil.get_terminal_size().columns
  except Exception:
    cols = 80
  width: int = max(cols - 1, 0)
  print("\r" + (" " * width) + "\r", end="", flush=True)


def run_countdown(seconds: int = 3) -> None:
  for remaining in range(seconds, 0, -1):
    print(f' {"-" * 3 + str(remaining) + "-" * 3} ', end="\r", flush=True)
    sleep_with_cancel(1.0)


while True:
  string = input("> ")
  if string.lower() in ["exit", "quit"]:
    break
  wpm = random.randint(100, 120)
  try:
    run_countdown(3)
    clear_status_line()
    Typer.legitTyper(string, wpm)
  except CancelRequested:
    clear_status_line()
    print("\r[Cancelled]", end="\n", flush=True)
    continue

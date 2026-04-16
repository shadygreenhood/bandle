import os
from sys import argv

from rich.console import Console
from rich.text import Text

# ╭---------------------------------╮
# |      ╭  ╮  ╭=-  ╭    ╭==╮       |
# |      ╞--╡  ╞-   |    ╞==╯       |
# |      ╰  ╯  ╰=-  ╰-╯  ╰          |
# ╰---------------------------------╯
def help(error=""):
    print(f"")
    print(str(error))
    print("\n" \
    "this script is the GUI for the shadygreenhood bandle project\n" \
    "\n" \
    "Usage: mixer2.py [option]=[value] [option2]=[value2] ... \n" \
    "\n" \
    "\n" \
    "Options:\n" \
    "--scale        final render scale of the window (0 to 1)\n" \
    "\n" \
    "\n")
    raise Exception(str(error))

# ╭--------------------------------------╮
# |      ╭=-╮  ╭    ╭=-  ╭==╮  ╭==╮      |
# |      |     |    ╞-   ╞--╡  ╞=:╯      |
# |      ╰=-╯  ╰-╯  ╰=-  ╰  ╯  ╰  ╰      |
# ╰--------------------------------------╯
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# ╭--------------------------------------------------------------╮
# |        ╭     ╭----╮ ╭----  ╭----  ╭---- ╭----╮ ╭----╮        |
# |        |     |    | |      |      |     |    | |    |        |
# |        |     |    | |    ╮ |    ╮ ╞--   ╞---╮╯ ╰----╮        |
# |        |     |    | |    | |    | |     |   ╰╮ |    |        |
# |        ╰---╯ ╰----╯ ╰----╯ ╰----╯ ╰---- ╰    ╯ ╰----╯        |
# ╰--------------------------------------------------------------╯

# ╭----------------------------------------------------------------------------╮
# |      ╭=-.  ╭==╮  ╭==╮  .  ╭=-╮       ╭    ╭==╮  ╭==╮  ╭==╮  ╭=-  ╭==╮      |
# |      ╞-:╯  ╞--╡  ╰--╮  |  |          |    |  |  |  ╮  |  ╮  ╞-   ╞=:╯      |
# |      ╰=-╯  ╰  ╯  ╰==╯  ╯  ╰=-╯       ╰-╯  ╰==╯  ╰==╯  ╰==╯  ╰=-  ╰  ╰      |
# ╰----------------------------------------------------------------------------╯
console = Console()
class logger():
    def debug(msg):
        console.print(f"[DEBUG]: {msg}", style="blue")
    def pretty_text(msg, style):
        console.print(msg, style=style)
    def warning(msg):
        console.print(f"[WARNING]: {msg}", style="yellow")
    def error(msg):
        console.print(f"[ERROR]: {msg}", style="bold red")


# ╭----------------------------------------------------------------------------------╮
# |      ╮ ╭  ╭==╮       ╭-.   ╭    ╭==╮       ╭    ╭==╮  ╭==╮  ╭==╮  ╭=-  ╭==╮      |
# |      ╰╮╯   ||   ---  |  |  |    ╞==╯       |    |  |  |  ╮  |  ╮  ╞-   ╞=:╯      |
# |       ╯    ╰╯        ╰='   ╰-╯  ╰          ╰-╯  ╰==╯  ╰==╯  ╰==╯  ╰=-  ╰  ╰      |
# ╰----------------------------------------------------------------------------------╯
class YTDLPLogger:
        def debug(self, msg):
            logger.debug(f"[DEBUG] {msg}")

        def warning(self, msg):
            logger.warning(f"[WARNING] {msg}")

        def error(self, msg):
            logger.error(f"[ERROR] {msg}")

def duration_filter(info, *, incomplete):
    duration = info.get("duration")
    
    if duration is None:
        return None  # allow if unknown
    
    if duration > 600:
        return "Video longer than 10 minutes"
    
    return None


# ╭------------------------------------------------------------------------------------╮
# |      ╭-.   ╭=-  ╭╮╭╮  ╭  ╮  ╭=-╮  ╭==╮       ╭    ╭==╮  ╭==╮  ╭==╮  ╭=-  ╭==╮      |
# |      |  |  ╞-   |╰╯|  |  |  |     ╰--╮       |    |  |  |  ╮  |  ╮  ╞-   ╞=:╯      |
# |      ╰='   ╰=-  ╰  ╯  ╰==╯  ╰=-╯  ╰==╯       ╰-╯  ╰==╯  ╰==╯  ╰==╯  ╰=-  ╰  ╰      |
# ╰------------------------------------------------------------------------------------╯
class DemucsLogger:
        def warning(self, msg):
            logger.warning(f"[DEMUCS] [WARNING] {msg}")

        def error(self, msg):
            logger.error(f"[DEMUCS] [ERROR] {msg}")


from io import StringIO
import re
progress_pattern = re.compile(r"(\d+)%")  # capture percentage from tqdm-like output

class ProgressCapture(StringIO):
                    """Capture stderr and extract progress percentage"""
                    def __init__(self, mode, out_vector):
                        self.mode = mode
                        super().__init__()
                        self.last_percent = 0 
                        self.out_vector = out_vector
                    def write(self, s):
                        super().write(s)
                        match = progress_pattern.search(s)
                        if match:
                            percent = int(match.group(1))
                            if percent != self.last_percent:
                                # print your custom bar
                                if self.mode == "live":
                                    self.out_vector.update(pacman_bar(percent, 50, 100))
                                elif self.mode == "wrapped":
                                    self.out_vector.pretty_text("[PROGRESS BAR]"+str(pacman_bar(percent, 45, 100), wrapped=True), "magenta")
                                self.last_percent = percent



# ╭--------------------------------------------------------------------------------╮
# |      ╭==╮  ╭==╮  ╭==╮  ╭==╮  ╭==╮  ╭=-  ╭==╮  ╭==╮       ╭=-.  ╭==╮  ╭==╮      |
# |      ╞==╯  ╞=:╯  |  |  |  ╮  ╞=:╯  ╞-   ╰--╮  ╰--╮       ╞-:╯  ╞--╡  ╞=:╯      |
# |      ╰     ╰  ╰  ╰==╯  ╰==╯  ╰  ╰  ╰=-  ╰==╯  ╰==╯       ╰=-╯  ╰  ╯  ╰  ╰      |
# ╰--------------------------------------------------------------------------------╯
def pacman_bar(step, width, maxsteps, wrapped=False):

    progress = step / maxsteps
    pos = int((width - 2) * progress)
    frame = int(2 * (width - 2) * progress) % 2
    text = Text()
    # opening bracket

    text.append("[", style="magenta")
    if pos >= (width - 2):
        text.append("-" * (width - 2), style="magenta")
        text.append("]", style="magenta")
        if wrapped:
            text.append(f"[cyan] 100%[/cyan]", style="magenta")
        else:
            text.append(f" 100%", style="cyan italic dim")
        print(text)
        return text
    # eaten part
    text.append("-" * pos, style="magenta")
    # pacman
    pac = "c" if frame == 0 else "C"
    if wrapped:
        text.append("[black]"+pac+"[/black]", style="magenta")
    else:
        text.append(pac, style="bold pink")
    # remaining pattern
    remaining = (width - 2) - pos - 1
    for i in range(int(remaining)):
        if (i + pos) % 2 == 0:
            text.append("o", style="magenta dim")
        else:
            text.append(" ")
    # closing bracket
    text.append("]", style="magenta")
    # percentage
    percent = progress * 100
    if wrapped:
        text.append(f"[cyan] {percent:.1f}%[/cyan]", style="magenta")
    else: 
        text.append(f" {percent:.1f}%", style="cyan italic dim")

    return text
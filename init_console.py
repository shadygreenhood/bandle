import os
from rich.live import Live
from rich.console import Console
from rich.text import Text


def clear():
    os.system("cls" if os.name == "nt" else "clear")

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



def pacman_bar(step, width, maxsteps):

    progress = step / maxsteps
    pos = int((width - 2) * progress)
    frame = int(2 * (width - 2) * progress) % 2
    text = Text()
    # opening bracket
    text.append("[", style="magenta")
    if pos >= (width - 2):
        text.append("-" * (width - 2), style="magenta")
        text.append("]", style="magenta")
        text.append(f" 100%", style="cyan italic dim")
        return text
    # eaten part
    text.append("-" * pos, style="magenta")
    # pacman
    pac = "c" if frame == 0 else "C"
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
    text.append(f" {percent:.1f}%", style="cyan italic dim")

    return text
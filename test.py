

from rich.live import Live
from rich.text import Text
import time

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

if __name__ == "__main__":
    # Demo
    width = 50
    maxsteps = 30

    with Live("", refresh_per_second=10) as live:
        for step in range(maxsteps + 1):
            live.update(pacman_bar(step, width, maxsteps))
            time.sleep(0.1)

    width = 100
    maxsteps = 30

    with Live("", refresh_per_second=10) as live:
        for step in range(maxsteps + 1):
            live.update(pacman_bar(step, width, maxsteps))
            time.sleep(0.1)

    width = 20
    maxsteps = 30

    with Live("", refresh_per_second=10) as live:
        for step in range(maxsteps + 1):
            live.update(pacman_bar(step, width, maxsteps))
            time.sleep(0.1)
from matplotlib import pyplot as plt
import numpy as np

from util.position import Position2D

def render_position(pos: Position2D, color):
    plt.arrow(
        pos.x, pos.y, pos.sin, pos.cos, head_width=5, head_length=5, fc=color, ec=color, alpha=0.5
    )
    plt.plot(pos.x, pos.y, "b.", markersize=4, color=color)
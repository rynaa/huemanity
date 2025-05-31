"""Generates pattern for a particular number."""

import pygame
import pygame.gfxdraw
from constants import *


def create_number_image(number, config, output_folder):
    """
    Generates an image of a given number centered on a black background.

    Args:
        number (int or str): The number to render on the image.
        config (dict): A dictionary containing font configuration settings,
                       e.g., "font_face", "font_size", "is_bold", "is_italic".
        output_folder (str): The directory where the generated image will be saved.

    Returns:
        str: The full path to the saved number mask image.
    """
    image_width, image_height = DISPLAY_SIZE, DISPLAY_SIZE
    background_color = BLACK

    screen = pygame.Surface((image_width, image_height))
    screen.fill(background_color)

    font = pygame.font.SysFont(config["font_face"], config["font_size"], config["is_bold"], config["is_italic"])
    text_surface = font.render(str(number), True, WHITE)
    text_width, text_height = font.size(str(number))
    center_x = (image_width - text_width) / 2
    center_y = (image_height - text_height) / 2
    screen.blit(text_surface, (center_x, center_y))

    output_filename = f'{output_folder}/number_mask.png'
    pygame.image.save(screen, output_filename)

    return output_filename
"""Generates pattern for a reference image."""

import math
import pygame
import pygame.gfxdraw
import random
from constants import *


def apply_color_shift(color, shift_range):
    """
    Shifts each RGB component of a color randomly within a given range.

    Args:
        color (tuple): The input color as an RGB tuple.
        shift_range (int): The maximum range to shift each color component.

    Returns:
        tuple: The new color with shifted RGB components.
    """
    shifted_color = list(color)
    for i in range(3):
        new_component = random.randint(shifted_color[i] - shift_range, shifted_color[i] + shift_range)
        shifted_color[i] = int(max(0, min(255, new_component)))
    return tuple(shifted_color)


def apply_light_shift(color, modifier_range):
    """
    Adjusts the lightness of a color by a random modifier.

    Args:
        color (tuple): The input color as an RGB tuple.
        modifier_range (float): The range for the lightness modifier.
                                If < 1, it's inverted to ensure a proper range.

    Returns:
        tuple: The new color with adjusted lightness.
    """
    shifted_color = list(color)
    actual_modifier_range = 1 / modifier_range if modifier_range < 1 else modifier_range
    modifier = random.uniform(1 / actual_modifier_range, actual_modifier_range)

    for i in range(3):
        shifted_color[i] = int(min(255, shifted_color[i] * modifier))
    return tuple(shifted_color)


def apply_gradient_shift(start_color, end_color, gradient_magnitude):
    """
    Shifts a color towards a second color based on a gradient magnitude.

    Args:
        start_color (tuple): The initial color.
        end_color (tuple): The color to shift towards.
        gradient_magnitude (float): How much to shift towards the end_color (0 to 1).

    Returns:
        tuple: The color after applying the gradient shift.
    """
    shifted_color = list(start_color)
    gradient_change = random.uniform(0, gradient_magnitude)

    for i in range(3):
        difference = start_color[i] - end_color[i]
        shifted_color[i] = int(start_color[i] - (difference * gradient_change))

    return tuple(shifted_color)


class Circle:
    """Represents a single circle in the pattern."""

    def __init__(self, x, y, radius, is_black_pixel):
        """
        Initializes a Circle object.

        Args:
            x (int): The x-coordinate of the circle's center.
            y (int): The y-coordinate of the circle's center.
            radius (int): The radius of the circle.
            is_black_pixel (bool): True if the circle corresponds to a black pixel in the reference image.
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.is_black_pixel = is_black_pixel

    def draw(self, surface, reference_color, config):
        """
        Draws the circle on the given surface based on configuration.

        Args:
            surface (pygame.Surface): The surface to draw the circle on.
            reference_color (tuple): The original color from the reference image.
            config (dict): A dictionary containing configuration settings for color effects.
        """
        if self.is_black_pixel:
            selected_color = config["first_color"]
            other_color = config["second_color"]
        else:
            selected_color = config["second_color"]
            other_color = config["first_color"]
        if config["do_gradientshift"]:
            selected_color = apply_gradient_shift(selected_color, other_color, config["gradient_range"])

        if config["do_colorshift"]:
            selected_color = apply_color_shift(selected_color, config["shifting_range"])
        if config["do_lightshift"]:
            selected_color = apply_light_shift(selected_color, config["modify_range"])

        pygame.gfxdraw.aacircle(surface, self.x, self.y, self.radius, selected_color)
        pygame.gfxdraw.filled_circle(surface, self.x, self.y, self.radius, selected_color)


def get_reference_pixel_data(reference_image, scaling_factor_x, scaling_factor_y):
    """
    Selects a random pixel from the reference image and returns its color and corresponding state.

    Args:
        reference_image (pygame.Surface): The reference image.
        scaling_factor_x (float): Scaling factor for x-coordinates.
        scaling_factor_y (float): Scaling factor for y-coordinates.

    Returns:
        tuple: A tuple containing (display_x, display_y, reference_color, is_black_pixel).
    """
    ref_image_width, ref_image_height = reference_image.get_size()
    random_x = random.randint(0, ref_image_width - 1)
    random_y = random.randint(0, ref_image_height - 1)

    display_x = int(random_x / scaling_factor_x)
    display_y = int(random_y / scaling_factor_y)
    reference_color = reference_image.get_at((random_x, random_y))
    is_black_pixel = (reference_color == BLACK)
    return display_x, display_y, reference_color, is_black_pixel


def calculate_max_circle_radius(center_x, center_y, outer_radius, middle_point, grid_matrix, min_radius, max_radius):
    """
    Calculates the largest possible radius for a new circle at a given position,
    considering outer bounds and collisions with existing circles.

    Args:
        center_x (int): The x-coordinate of the potential new circle's center.
        center_y (int): The y-coordinate of the potential new circle's center.
        outer_radius (float): The radius of the outer bounding circle.
        middle_point (tuple): The (x, y) coordinates of the center of the outer circle.
        grid_matrix (list): A 2D list representing the grid of existing circles.
        min_radius (int): The minimum allowed radius for a circle.
        max_radius (int): The maximum allowed radius for a circle.

    Returns:
        int: The calculated maximum possible radius, or a value less than min_radius if no valid radius exists.
    """
    distance_to_origin = math.dist((center_x, center_y), middle_point)
    biggest_possible_radius = outer_radius - distance_to_origin

    if biggest_possible_radius < min_radius:
        return 0

    # Check for collisions with existing circles in the grid
    x_grid_indices = [
        (center_x // (2 * max_radius)) + i
        for i in [-1, 0, 1]
    ]
    y_grid_indices = [
        (center_y // (2 * max_radius)) + i
        for i in [-1, 0, 1]
    ]

    for x_idx in x_grid_indices:
        for y_idx in y_grid_indices:
            # Ensure indices are within bounds
            if 0 <= x_idx < len(grid_matrix) and 0 <= y_idx < len(grid_matrix[0]):
                current_square_circles = grid_matrix[x_idx][y_idx]
                for existing_circle in current_square_circles:
                    distance_between_centers = math.dist((center_x, center_y), (existing_circle.x, existing_circle.y))
                    # The current_radius is the distance between centers minus the existing circle's radius.
                    # This represents the maximum radius for the new circle without overlapping.
                    current_radius_no_overlap = distance_between_centers - existing_circle.radius
                    biggest_possible_radius = min(biggest_possible_radius, current_radius_no_overlap)

                    if biggest_possible_radius < min_radius:
                        return 0  # No valid radius found if it's too small

    return int(min(biggest_possible_radius, max_radius))


def main(image_location, config, output_folder):
    """
    Generates a circular pattern based on a reference image, applying various visual effects.

    Args:
        image_location (str): Path to the reference image.
        config (dict): Configuration dictionary for pattern generation.
        output_folder (str): Folder to save the generated image.

    Returns:
        str: The file path of the generated output image.
    """
    display_width, display_height = DISPLAY_SIZE, DISPLAY_SIZE
    screen_center = (display_width / 2, display_height / 2)
    outer_circle_radius = DISPLAY_SIZE / 2

    screen = pygame.Surface((display_width, display_height))
    screen.fill(WHITE)

    reference_image = pygame.image.load(image_location)
    ref_image_width, ref_image_height = reference_image.get_size()
    scaling_factor_x = ref_image_width / display_width
    scaling_factor_y = ref_image_height / display_height

    # Initialize a grid to efficiently store and check for circle collisions
    grid_rows = (display_width // (2 * config["max_radius"])) + 2
    grid_cols = (display_height // (2 * config["max_radius"])) + 2
    grid_matrix = [[[] for _ in range(grid_cols)] for _ in range(grid_rows)]

    for _ in range(ITERATIONS):
        display_x, display_y, reference_color, is_black_pixel = \
            get_reference_pixel_data(reference_image, scaling_factor_x, scaling_factor_y)

        # Skip if a circle has already been drawn at this pixel
        if screen.get_at((display_x, display_y)) != WHITE:
            continue

        max_allowed_radius = calculate_max_circle_radius(
            display_x, display_y, outer_circle_radius, screen_center,
            grid_matrix, config["min_radius"], config["max_radius"]
        )

        if max_allowed_radius >= config["min_radius"]:
            new_circle = Circle(display_x, display_y, max_allowed_radius, is_black_pixel)
            
            # Add the new circle to the appropriate grid cell
            grid_cell_x = display_x // (2 * config["max_radius"])
            grid_cell_y = display_y // (2 * config["max_radius"])
            grid_matrix[grid_cell_x][grid_cell_y].append(new_circle)
            
            new_circle.draw(screen, reference_color, config)

    output_filepath = f'{output_folder}/ishihara.png'
    pygame.image.save(screen, output_filepath)
    return output_filepath
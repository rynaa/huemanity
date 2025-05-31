"""Main function to generate dataset."""

import itertools
import os
import json
import string
import uuid
from constants import *
import image_to_pattern_generator
import number_to_pattern_generator
from tqdm import tqdm
import pygame


DEFAULT_CONFIG = {
    "min_radius": 4,
    "max_radius": 15,
    "shifting_range": 30,
    "modify_range": 1.5,
    "gradient_range": 0.3,
    "do_colorshift": True,
    "do_lightshift": True,
    "do_gradientshift": True,
    "value": 12,
    "first_color": CADET_BLUE,
    "second_color": ROSY_BROWN,
    "first_color_name": "CadetBlue",
    "second_color_name": "RosyBrown",
    "font_face": "DejaVu Sans",
    "font_size": 550,
    "is_bold": True,
    "is_italic": True,
    "contrast_type": None,
    "is_number": None,
}


def generate_two_char_alphanumerics():
    """
    Generates a list of all two-character alphanumeric combinations,
    excluding specific characters ("l", "I", "J", "O") and numbers starting with "0".
    """
    chars = list(set(string.ascii_letters + string.digits) - {'l', 'I', 'J', 'O'})
    all_combinations = [''.join(pair) for pair in itertools.product(chars, repeat=2)]
    combinations_to_remove = [f"0{i}" for i in range(10)]
    filtered_combinations = [
        combo for combo in all_combinations if combo not in combinations_to_remove
    ]
    return filtered_combinations


def generate_patterns_for_contrast_pairs(output_path, color_pairs):
    """
    Generates pattern images for various alphanumeric combinations using different
    medium contrast color pairs.

    Args:
        output_path (str): The base directory to save the generated dataset.
        color_pairs (dict): A dictionary where keys are color pair names (e.g., "Color1_Color2")
                                 and values are tuples of [color1_rgb, color2_rgb].
    """
    alphanumeric_combinations = generate_two_char_alphanumerics()

    for char_combo in tqdm(alphanumeric_combinations):
        for color_pair_name in color_pairs:
            config = DEFAULT_CONFIG.copy()
            current_image_id = uuid.uuid4()
            config["value"] = char_combo
            config["first_color"] = color_pairs[color_pair_name][0]
            config["second_color"] = color_pairs[color_pair_name][1]
            config["first_color_name"], config["second_color_name"] = color_pair_name.split('_')
            config["contrast_type"] = "medium"
            config["is_number"] = char_combo.isdigit()

            output_folder = os.path.join(output_path, str(current_image_id))
            os.makedirs(output_folder, exist_ok=True)

            number_mask_path = number_to_pattern_generator.create_number_image(
                config["value"], config, output_folder
            )
            image_to_pattern_generator.main(number_mask_path, config, output_folder)

            config_filepath = os.path.join(output_folder, 'config.json')
            with open(config_filepath, "w") as f:
                json.dump(config, f, indent=4)


if __name__ == "__main__":
    output_path = f"results/"
    os.makedirs(output_path, exist_ok=True)
    pygame.init()
    generate_patterns_for_contrast_pairs(output_path, MEDIUM_CONTRAST_COLORS)
    pygame.quit()

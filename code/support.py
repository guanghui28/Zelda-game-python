from csv import reader
from os import walk
import pygame # type:ignore

def import_csv_layout(path):
    with open(path) as level_map:
        terrain_map = [list(row) for row in reader(level_map)]
    return terrain_map

def import_folder(path):
    for _,__,img_files in walk(path):
        surface_list = [pygame.image.load(f'{path}/{image}').convert_alpha() 
                        for image in img_files ]
    return surface_list
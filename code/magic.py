import pygame # type: ignore
from settings import *
from random import randint

class MagicPlayer():
    def __init__(self,animation_player):
        self.animation_player = animation_player
        self.sounds = {
            'heal': pygame.mixer.Sound('../audio/heal.wav'),
            'flame': pygame.mixer.Sound('../audio/fire.wav'),
        }
        
    def heal(self, player, strength, cost, groups):
        if player.energy >= cost:
            self.sounds['heal'].play()
            player.health += strength
            player.energy -= cost
            if player.health > player.stats['health']:
                player.health = player.stats['health']
            self.animation_player.create_particles('aura',player.rect.center, groups)
            self.animation_player.create_particles('heal',player.rect.center + pygame.math.Vector2(0,-60), groups)
                    
    def flame(self,player,cost,groups):
        if player.energy >= cost:
            player.energy -= cost
            self.sounds['flame'].play()
            # get direction from status player
            player_status = player.status.split("_")[0]
            if  player_status == 'right': direction = pygame.math.Vector2((1, 0))
            elif  player_status == 'left': direction = pygame.math.Vector2((-1, 0))
            elif  player_status == 'up': direction = pygame.math.Vector2((0, -1))
            else: direction = pygame.math.Vector2((0, 1))
            
            # from direction create 5 block from the player
            for i in range(1, 6):
                if direction.x: # horizontal
                    offset_x = (direction.x * i) * TILE_SIZE
                    x = player.rect.centerx + offset_x + randint(-TILE_SIZE//3,TILE_SIZE//3)
                    y = player.rect.centery + randint(-TILE_SIZE//3,TILE_SIZE//3)
                    self.animation_player.create_particles('flame', (x, y), groups)
                else: # vertical
                    offset_y = (direction.y * i) * TILE_SIZE
                    x = player.rect.centerx + randint(-TILE_SIZE//3,TILE_SIZE//3)
                    y = player.rect.centery + offset_y + randint(-TILE_SIZE//3,TILE_SIZE//3)
                    self.animation_player.create_particles('flame', (x, y), groups)
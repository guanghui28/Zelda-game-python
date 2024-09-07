import pygame # type: ignore
from settings import *
from entity import Entity
from support import import_folder

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprite):
        super().__init__(groups)
        
        # general setup
        self.sprite_type = 'enemy'
        
        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        
        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprite
        
        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        
        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 800
        
    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'../graphics/monsters/{name}'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(f'{main_path}/{animation}')
            
    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        direction = (player_vec - enemy_vec).normalize() if distance > 0 else pygame.math.Vector2()
        return (distance, direction)
            
    def get_status(self, player):
        distance, _ = self.get_player_distance_direction(player)
        
        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
                
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
            
    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else: # player moving out the attack circle
            self.direction = pygame.math.Vector2()
    
    def cooldown(self):
        current_timer = pygame.time.get_ticks()
        if not self.can_attack:
            if current_timer - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
         
    def animate(self):
        animations = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animations):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
        
        self.image = animations[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
            
    def update(self):
        self.movement(self.speed)
        self.animate()
        self.cooldown()
        
    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
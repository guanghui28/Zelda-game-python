import pygame # type: ignore
from settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
		super().__init__(groups)
		self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, -26)
		# graphics set up
		self.import_player_assets()
		self.status = 'down'
		self.frame_index = 0
		self.animation_speed = 0.15
  
		# movement
		self.direction = pygame.math.Vector2()
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None
  
		self.obstacle_sprites = obstacle_sprites
  
		# weapon
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.weapon_index = 0
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 200
  
		# magic
		self.create_magic = create_magic
		self.magic_index = 0
		self.magic = list(magic_data.keys())[self.magic_index]
		self.can_switch_magic = True
		self.magic_switch_time = None
  
		# stats
		self.stats = {'health':100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
		self.health = self.stats['health'] * 0.5
		self.energy = self.stats['energy'] * 0.8
		self.exp = 123
		self.speed = self.stats['speed']
  
	def import_player_assets(self):
		character_path = '../graphics/player'
		self.animations = {
			'up': [],'down': [], 'left': [], 'right':[], 
   			'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [], 
      		'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
		}

		for animation in self.animations.keys():
			full_path = f'{character_path}/{animation}'
			self.animations[animation] = import_folder(full_path)
  	
	def get_input(self):
		# don't do anything when attacking
		if not self.attacking:
			keys = pygame.key.get_pressed()
	
			# movement input
			if keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.status = 'left'
			elif keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.status = 'right'
			else:
				self.direction.x = 0
	
			if keys[pygame.K_UP]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0
	
			# attack input
			if keys[pygame.K_SPACE]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack()
	
			# magic input
			if keys[pygame.K_LCTRL]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				strength = magic_data[self.magic]['strength']  + self.stats['magic']
				cost = magic_data[self.magic]['cost']
				self.create_magic(self.magic, strength, cost)
    
			# choose weapon
			if keys[pygame.K_q] and self.can_switch_weapon:
				self.can_switch_weapon = False
				self.weapon_switch_time = pygame.time.get_ticks()
				self.weapon_index = (self.weapon_index + 1) % len(weapon_data.keys())
				self.weapon = list(weapon_data.keys())[self.weapon_index]
    
			# choose magic
			if keys[pygame.K_e] and self.can_switch_magic:
				self.can_switch_magic = False
				self.magic_switch_time = pygame.time.get_ticks()
				self.magic_index = (self.magic_index + 1) % len(magic_data.keys())
				self.magic = list(magic_data.keys())[self.magic_index]

	def movement(self, speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
		
		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center
  
	def get_status(self):
		# idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = f'{self.status}_idle'

		# attack status
		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle', '_attack')
				else:
					self.status = f'{self.status}_attack'
		else:
			# attack done!
			if 'attack' in self.status:
				self.status = self.status.replace('_attack', '')

	def collision(self, direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0: # moving right
						self.hitbox.right = sprite.hitbox.left
					elif self.direction.x < 0: # moving left
						self.hitbox.left = sprite.hitbox.right
		elif direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0: # moving down
						self.hitbox.bottom = sprite.hitbox.top
					elif self.direction.y < 0: # moving up
						self.hitbox.top = sprite.hitbox.bottom
 
	def cooldown(self):
		current_time = pygame.time.get_ticks()
  
		if self.attacking:
			if current_time - self.attack_time > self.attack_cooldown:
				self.attacking = False
				self.destroy_attack()
    
		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time > self.switch_duration_cooldown:
				self.can_switch_weapon = True
    
		if not self.can_switch_magic:
			if current_time - self.magic_switch_time > self.switch_duration_cooldown:
				self.can_switch_magic = True
 
	def animate(self):
		animations_surface = self.animations[self.status]
		max_frame = len(animations_surface)
		# loop over the frame index
		self.frame_index += self.animation_speed
		# set image
		self.image = animations_surface[int(self.frame_index%max_frame)]
		self.rect = self.image.get_rect(center=self.hitbox.center)
 
	def update(self):
		self.get_input()
		self.cooldown()
		self.get_status()
		self.animate()
		self.movement(self.speed)
import pygame
from particles import ParticleEffect
from util import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile, Crate, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Clouds
from player import Player
from game_data import levels


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health):
        self.display_surface = surface
        self.world_shift = 0
        self.player_on_ground = False
        self.current_x = None

        # overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # user interface
        self.change_coins = change_coins
        self.change_health = change_health
        # explosion
        self.explosion_sprites = pygame.sprite.Group()

        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(
            terrain_layout, 'terrain')

        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crates')

        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        fg_palm_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palm_sprites = self.create_tile_group(
            fg_palm_layout, 'fg palms')

        bg_palm_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palm_sprites = self.create_tile_group(
            bg_palm_layout, 'bg palms')

        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(
            constraint_layout, 'constraints')

        self.sky = Sky(8)

        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 20, level_width)

        self.clouds = Clouds(400, level_width, 25)

        self.player_setup(enemy_layout, change_health)

    def player_setup(self, layout, change_health):
        self.player = pygame.sprite.GroupSingle()

        for row_idx, row in enumerate(layout):
            for col_idx, cell in enumerate(row):
                x = col_idx * tile_size
                y = row_idx * tile_size

                if cell == '2':
                    player_sprite = Player((x, y), change_health)
                    self.player.add(player_sprite)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_idx, row in enumerate(layout):
            for col_idx, cell in enumerate(row):
                if cell != '-1':
                    x = col_idx * tile_size
                    y = row_idx * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics(
                            "assets/graphics/terrain/terrain_tiles.png")
                        tile_surface = terrain_tile_list[int(cell)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics(
                            "assets/graphics/decoration/grass/grass.png")
                        tile_surface = grass_tile_list[int(cell)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    if type == 'coins':
                        if cell == '0': sprite = Coin(
                            tile_size, x, y, 'assets/graphics/coins/gold', 5)
                        if cell == '1': sprite = Coin(
                            tile_size, x, y, 'assets/graphics/coins/silver', 1)

                    if type == 'fg palms':
                        if cell == '0':
                            sprite = Palm(
                                tile_size, x, y, 'assets/graphics/terrain/palm_small', 38)
                        if cell == '2':
                            sprite = Palm(
                                tile_size, x, y, 'assets/graphics/terrain/palm_large', 64)

                    if type == 'bg palms':
                        if cell == '3':
                            sprite = Palm(tile_size, x, y, 'assets/graphics/terrain/palm_bg', 64)
                        if cell == '4':
                            tile_surface = pygame.image.load("assets/graphics/terrain/castle.png").convert_alpha()
                            sprite = StaticTile(tile_size, x, y, tile_surface)
                            
                    if type == 'enemies':
                        if cell == '0':
                            sprite = Enemy(tile_size, x, y)

                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def horizontal_mvt_coll(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        collidable_sprites = self.terrain_sprites.sprites(
        ) + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

    def vertical_mvt_coll(self):
        player = self.player.sprite
        player.apply_gravity()

        collidable_sprites = self.terrain_sprites.sprites(
        ) + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < (screen_width / 4) and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else: 
            self.player_on_ground = False

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_enemy_collision(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
        
        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top

                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

    def run(self):

        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)

        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)
        
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)
        
        self.coin_sprites.draw(self.display_surface)
        self.coin_sprites.update(self.world_shift)

        self.fg_palm_sprites.draw(self.display_surface)
        self.fg_palm_sprites.update(self.world_shift)
        
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        self.player.update()
        self.horizontal_mvt_coll()
        
        self.get_player_on_ground()
        self.vertical_mvt_coll()
        
        self.scroll_x()
        self.player.draw(self.display_surface)
        
        self.check_death()
        self.check_coin_collision()
        self.check_enemy_collision()

        self.water.draw(self.display_surface, self.world_shift)
        
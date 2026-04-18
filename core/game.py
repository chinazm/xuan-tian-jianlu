"""游戏主场景：整合所有系统，运行游戏逻辑。"""
import pygame
from core.scene_manager import Scene
from core.config import GameConfig
from core.vector import Vector2
from core.input_handler import InputHandler
from core.camera import Camera
from core.event_bus import EventBus
from core.resource_manager import ResourceManager
from world.tilemap import Tilemap
from world.room import Room
from entities.player import Player
from entities.enemy import Enemy
from systems.collision import CollisionSystem
from systems.combat import CombatSystem
from systems.cultivation import CultivationSystem
from systems.inventory import Inventory
from systems.dialogue import DialogueSystem
from systems.quest import QuestSystem
from systems.save_load import SaveData
from systems.particle import ParticleSystem
from systems.audio import AudioManager
from ui.hud import HUD


class GameScene(Scene):
    def __init__(self, config: GameConfig, room_id: str = "sect_main"):
        super().__init__("game")
        self._config = config
        self._room_id = room_id

        # 核心系统
        self.input = InputHandler()
        self.camera = Camera(config.window.width, config.window.height)
        self.camera.smoothing = config.render.camera_smooth
        self.resources = ResourceManager(base_path="assets")
        self.collision = CollisionSystem()
        self.combat = CombatSystem()
        self.cultivation = CultivationSystem()
        self.inventory = Inventory()
        self.dialogue = DialogueSystem()
        self.quest = QuestSystem()
        self.particles = ParticleSystem()
        self.audio = AudioManager()

        # 游戏状态
        self.player: Player = None
        self.enemies: list[Enemy] = []
        self.tilemap: Tilemap = None
        self.hud = HUD(config.window.width, config.window.height)
        self.paused = False
        self.play_time = 0.0

    def on_enter(self):
        super().on_enter()
        self._load_room(self._room_id)

    def _load_room(self, room_id: str):
        room = Room.from_json(f"maps/{room_id}.json")
        if not room:
            return
        self.tilemap = Tilemap(self.resources, self._config.render.tile_size)
        self.tilemap.load(f"maps/{room_id}.json", "tiles/tileset.png")
        self.camera.set_bounds(self.tilemap.pixel_width, self.tilemap.pixel_height)
        self.collision.set_terrain(self.tilemap.get_collision_rects())

        # 创建玩家
        if not self.player:
            self.player = Player(pos=Vector2(64, 64))
        else:
            self.player.pos = Vector2(64, 64)

        # 创建敌人
        self.enemies.clear()
        for e_data in room.enemies:
            pos = Vector2(e_data["pos"][0] * 32, e_data["pos"][1] * 32)
            enemy = Enemy(entity_id=f"{e_data['type']}_{len(self.enemies)}", pos=pos)
            self.enemies.append(enemy)

        for e in [self.player] + self.enemies:
            self.collision.add_entity(e)

        # 初始化任务
        self.quest.start_quest("MAIN_CH02_001")

        # 播放房间音乐
        if room.music:
            self.audio.play_music(f"assets/music/{room.music}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if event.key == pygame.K_F5:
                self._save_game()
            if event.key == pygame.K_F9:
                self._load_game()

    def update(self, dt):
        if self.paused:
            return
        self.play_time += dt
        self.input.update(dt)
        self.player.handle_input(self.input, dt)
        self.player.update(dt)
        self.collision.resolve_terrain(self.player)
        self.camera.follow(self.player.pos, dt)

        # 敌人AI
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            if enemy.can_see_player(self.player.pos, max_distance=200):
                enemy.start_chase(self.player.pos)
            elif enemy.state == "chase" and not enemy.can_see_player(self.player.pos, max_distance=250):
                enemy.stop_chase()
            enemy.update(dt)
            self.collision.resolve_terrain(enemy)

        # 战斗 - 攻击判定
        if self.player.state == "attack" and self.player.attack_timer <= self._config.combat.default_attack_cooldown * 0.5:
            hitbox = self.player.get_attack_rect()
            for enemy in self.enemies:
                if enemy.is_alive and hitbox.colliderect(enemy.get_collision_rect()):
                    enemy.take_damage(self.player.base_speed * 0.3, self.player.pos)

        # 战斗 - 投射物
        self.combat.update(dt, self.enemies)

        # 粒子
        self.particles.update(dt)

        # 事件驱动的更新
        EventBus.publish("update", {"dt": dt})

    def render(self, screen):
        screen.fill((20, 20, 30))
        if self.tilemap:
            self.tilemap.render(screen, self.camera)

        # 渲染敌人
        for enemy in self.enemies:
            if enemy.is_alive:
                enemy.render(screen, self.camera)

        # 渲染投射物
        for proj in self.combat.get_projectiles():
            if proj.is_alive:
                proj.render(screen, self.camera)

        # 渲染玩家
        if self.player:
            self.player.render(screen, self.camera)

        # 粒子
        self.particles.render(screen, self.camera)

        # HUD
        state = {
            "current_hp": self.player.current_hp, "max_hp": self.player.max_hp,
            "current_mp": self.cultivation.lingli, "max_mp": 100,
            "realm": self.cultivation.current_realm_name,
            "realm_level": self.cultivation.realm_level,
            "lingshi": self.inventory.lingshi,
            "skills": ["普通攻击", "御剑术"],
        }
        self.hud.render(screen, state)

        if self.paused:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

    def _save_game(self):
        data = SaveData(
            player_name="林凡",
            realm=self.cultivation.current_realm_name,
            realm_level=self.cultivation.realm_level,
            lingli=self.cultivation.lingli,
            max_hp=self.player.max_hp,
            current_hp=self.player.current_hp,
            current_room=self._room_id,
            player_pos=[self.player.pos.x, self.player.pos.y],
            lingshi=self.inventory.lingshi,
            play_time=self.play_time,
        )
        data.save(1)

    def _load_game(self):
        data = SaveData.load(1)
        if data:
            self.player.current_hp = data.current_hp
            self.player.max_hp = data.max_hp
            self.cultivation.current_realm_index = 0  # simplified
            self.cultivation.realm_level = data.realm_level
            self.cultivation.lingli = data.lingli

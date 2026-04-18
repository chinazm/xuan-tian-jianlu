"""游戏主场景：整合所有系统，运行游戏逻辑。"""
import pygame
from pathlib import Path
from core.scene_manager import Scene
from core.config import GameConfig
from core.vector import Vector2
from core.input_handler import InputHandler
from core.camera import Camera
from core.event_bus import EventBus
from core.resource_manager import ResourceManager
from core.touch_controller import TouchController
from core.performance import DynamicFPS
from core.android_adapter import AndroidAdapter

# Android 返回键映射 (python-for-android 的 android.keys 模块)
try:
    from android.keys import KEYCODE_BACK
    HAS_ANDROID_KEYS = True
except ImportError:
    KEYCODE_BACK = 4  # Android KEYCODE_BACK 默认值
    HAS_ANDROID_KEYS = False
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
from ui.dialogue_ui import DialogueUI
from ui.pause_menu import PauseMenu
from ui.inventory_ui import InventoryUI
from ui.cultivation_ui import CultivationUI
from ui.quest_ui import QuestUI


class GameState:
    """游戏状态枚举。"""
    PLAYING = "playing"
    PAUSED = "paused"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    CULTIVATION = "cultivation"
    QUEST = "quest"


class GameScene(Scene):
    def __init__(self, config: GameConfig, room_id: str = "sect_main", base_dir: Path = None):
        super().__init__("game")
        self._config = config
        self._room_id = room_id
        self._base_dir = base_dir
        self._android_env = False
        self._state = GameState.PLAYING
        
        # 核心系统
        self.input = InputHandler()
        self.camera = Camera(config.window.width, config.window.height)
        self.camera.smoothing = config.render.camera_smooth
        self.resources = ResourceManager(base_path="assets", base_dir=base_dir)
        self.collision = CollisionSystem()
        self.combat = CombatSystem()
        self.cultivation = CultivationSystem()
        self.inventory = Inventory()
        self.dialogue = DialogueSystem()
        self.quest = QuestSystem()
        self.particles = ParticleSystem()
        self.audio = AudioManager()
        
        # 触屏控制器
        self.touch = TouchController(config.window.width, config.window.height)
        self.input.set_touch_controller(self.touch)
        
        # 性能监控
        self.perf = DynamicFPS()
        
        # Android 系统适配器
        self.android = AndroidAdapter()
        if self.android.is_android():
            self.android.acquire_wakelock()
        
        # UI 组件
        self.hud = HUD(config.window.width, config.window.height)
        self.dialogue_ui = DialogueUI(config.window.width, config.window.height)
        self.pause_menu = PauseMenu(config.window.width, config.window.height)
        self.inventory_ui = InventoryUI(config.window.width, config.window.height)
        self.cultivation_ui = CultivationUI(config.window.width, config.window.height)
        self.quest_ui = QuestUI(config.window.width, config.window.height)
        
        # 游戏状态
        self.player: Player = None
        self.enemies: list[Enemy] = []
        self.tilemap: Tilemap = None
        self.paused = False
        self.play_time = 0.0

    def on_enter(self):
        super().on_enter()
        self._load_room(self._room_id)
        self._check_android()
    
    def _check_android(self):
        """检测 Android 环境。"""
        try:
            import android
            self._android_env = True
        except ImportError:
            self._android_env = False

    def _load_room(self, room_id: str):
        room = Room.from_json(f"maps/{room_id}.json")
        if not room:
            return
        self.tilemap = Tilemap(self.resources, self._config.render.tile_size)
        self.tilemap.load(f"maps/{room_id}.json", "tiles/tileset.png")
        self.camera.set_bounds(self.tilemap.pixel_width, self.tilemap.pixel_height)
        self.collision.set_terrain(self.tilemap.get_collision_rects())

        if not self.player:
            self.player = Player(pos=Vector2(64, 64))
            self.player._last_reported_hp = self.player.current_hp
        else:
            self.player.pos = Vector2(64, 64)
            self.player._last_reported_hp = self.player.current_hp

        self.enemies.clear()
        for e_data in room.enemies:
            pos = Vector2(e_data["pos"][0] * 32, e_data["pos"][1] * 32)
            enemy = Enemy(entity_id=f"{e_data['type']}_{len(self.enemies)}", pos=pos)
            self.enemies.append(enemy)

        for e in [self.player] + self.enemies:
            self.collision.add_entity(e)

        self.quest.start_quest("MAIN_CH02_001")

        if room.music:
            self.audio.play_music(f"assets/music/{room.music}")

    def _set_state(self, state: GameState):
        """切换游戏状态。"""
        self._state = state
    
    def _get_screen_pos(self, event) -> tuple:
        """从触摸事件获取屏幕坐标。"""
        return (event.dict['x'] * self._config.window.width,
                event.dict['y'] * self._config.window.height)
    
    def _route_touch(self, event):
        """将触摸事件路由到当前活动的 UI 组件。"""
        pos = self._get_screen_pos(event)
        
        if self._state == GameState.PAUSED:
            self.pause_menu.handle_touch(pos, event.type)
        elif self._state == GameState.DIALOGUE:
            self.dialogue_ui.handle_touch(pos, event.type)
        elif self._state == GameState.INVENTORY:
            self.inventory_ui.handle_touch(pos, event.type)
        elif self._state == GameState.CULTIVATION:
            self.cultivation_ui.handle_touch(pos, event.type)
        elif self._state == GameState.QUEST:
            self.quest_ui.handle_touch(pos, event.type)
        else:
            # 游戏进行中：HUD 和 触摸控制器
            self.hud.handle_touch(pos, event.type)
            self.touch.handle_event(event)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._state == GameState.PLAYING:
                    self._set_state(GameState.PAUSED)
                elif self._state == GameState.PAUSED:
                    self._set_state(GameState.PLAYING)
                else:
                    self._set_state(GameState.PLAYING)
            elif event.key == pygame.K_F5:
                self._save_game()
            elif event.key == pygame.K_F9:
                self._load_game()
        
        # Android 返回键处理
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_AC_BACK:  # Android BACK 键
                if self._state == GameState.PLAYING:
                    self._set_state(GameState.PAUSED)
                elif self._state == GameState.PAUSED:
                    self._set_state(GameState.PLAYING)
                elif self._state in (GameState.DIALOGUE, GameState.INVENTORY,
                                     GameState.CULTIVATION, GameState.QUEST):
                    self._set_state(GameState.PLAYING)
        
        # 触屏事件路由
        if self._android_env and event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self._route_touch(event)
    
    def _handle_ui_actions(self):
        """处理 UI 组件产生的动作请求。"""
        # 暂停菜单动作
        if self._state == GameState.PAUSED:
            action = self.pause_menu.selected_action
            if action == "resume":
                self._set_state(GameState.PLAYING)
            elif action == "save":
                slot = self.pause_menu.selected_slot
                if slot:
                    self._save_game(slot)
            elif action == "load":
                slot = self.pause_menu.selected_slot
                if slot:
                    self._load_game(slot)
            elif action == "cultivate":
                self._set_state(GameState.CULTIVATION)
            elif action == "inventory":
                self._set_state(GameState.INVENTORY)
            elif action == "quest":
                self._set_state(GameState.QUEST)
            elif action == "quit":
                self.player.is_alive = False  # 触发退出
        
        # 对话选项
        if self._state == GameState.DIALOGUE:
            choice_idx = self.dialogue_ui.get_selected_choice()
            if choice_idx is not None:
                next_id = self.dialogue.next(choice_idx)
                if next_id:
                    self.dialogue.start(next_id)
                else:
                    self._set_state(GameState.PLAYING)
            elif not self.dialogue.has_choices():
                # 无选项时点击推进对话
                # 通过触摸位置判断是否是"点击继续"
                # 简化：直接推进
                next_id = self.dialogue.next()
                if next_id:
                    self.dialogue.start(next_id)
                else:
                    self.dialogue.end()
                    self._set_state(GameState.PLAYING)
        
        # 背包关闭
        if self._state == GameState.INVENTORY:
            if self.inventory_ui.selected_item_index is not None:
                pass  # 可选：使用物品
            
        # 修炼突破
        if self._state == GameState.CULTIVATION:
            if self.cultivation_ui.breakthrough_requested:
                self.cultivation.add_lingli(0)  # 触发突破检查
        
        # 关闭所有子 UI 回到游戏
        if self._state in (GameState.INVENTORY, GameState.CULTIVATION, GameState.QUEST):
            if self._state == GameState.INVENTORY:
                inv = self.inventory_ui
            elif self._state == GameState.CULTIVATION:
                inv = self.cultivation_ui
            else:
                inv = self.quest_ui
            
            # 检查关闭按钮触摸（已在其 handle_touch 中处理）
            if hasattr(inv, '_close_btn') and inv._close_btn._pressed:
                self._set_state(GameState.PLAYING)

    def update(self, dt):
        # 性能监控
        if self.perf:
            self.perf.update(dt)
        
        if self._state == GameState.PAUSED:
            self.pause_menu.reset()
            return
        if self._state in (GameState.INVENTORY, GameState.CULTIVATION, GameState.QUEST, GameState.DIALOGUE):
            self._handle_ui_actions()
            return
        
        self.play_time += dt
        
        if self._android_env:
            self.touch.update(dt)
            self.touch.reset_just_pressed()
        
        self.input.update(dt)
        self.player.handle_input(self.input, dt)
        self.player.update(dt)
        self.collision.resolve_terrain(self.player)
        self.camera.follow(self.player.pos, dt)

        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            if enemy.can_see_player(self.player.pos, max_distance=200):
                enemy.start_chase(self.player.pos)
            elif enemy.state == "chase" and not enemy.can_see_player(self.player.pos, max_distance=250):
                enemy.stop_chase()
            enemy.update(dt)
            self.collision.resolve_terrain(enemy)

        if self.player.state == "attack" and self.player.attack_timer <= self._config.combat.default_attack_cooldown * 0.5:
            hitbox = self.player.get_attack_rect()
            for enemy in self.enemies:
                if enemy.is_alive and hitbox.colliderect(enemy.get_collision_rect()):
                    enemy.take_damage(self.player.base_speed * 0.3, self.player.pos)
                    # 攻击命中震动反馈
                    self.android.vibrate(50)

        self.combat.update(dt, self.enemies)
        self.particles.update(dt)
        
        # 检测敌人死亡，触发短震动
        for enemy in self.enemies:
            if not enemy.is_alive and not hasattr(enemy, '_death_notified'):
                enemy._death_notified = True
                self.android.vibrate(80)
        
        # 检测玩家受击，触发长震动
        if self.player.current_hp < self.player._last_reported_hp:
            self.android.vibrate(150)
        self.player._last_reported_hp = self.player.current_hp
        
        EventBus.publish("update", {"dt": dt})

    def render(self, screen):
        screen.fill((20, 20, 30))
        if self.tilemap:
            self.tilemap.render(screen, self.camera)

        for enemy in self.enemies:
            if enemy.is_alive:
                enemy.render(screen, self.camera)

        for proj in self.combat.get_projectiles():
            if proj.is_alive:
                proj.render(screen, self.camera)

        if self.player:
            self.player.render(screen, self.camera)

        self.particles.render(screen, self.camera)

        # HUD（始终渲染，除非在子 UI 中）
        if self._state == GameState.PLAYING:
            state = {
                "current_hp": self.player.current_hp, "max_hp": self.player.max_hp,
                "current_mp": self.cultivation.lingli, "max_mp": 100,
                "realm": self.cultivation.current_realm_name,
                "realm_level": self.cultivation.realm_level,
                "lingshi": self.inventory.lingshi,
                "skills": ["普通攻击", "御剑术"],
            }
            self.hud.render(screen, state)
        
        # Android 触摸层
        if self._android_env and self._state == GameState.PLAYING:
            self.touch.render(screen)
        
        # 子 UI 覆盖
        if self._state == GameState.PAUSED:
            self.pause_menu.render(screen)
        elif self._state == GameState.DIALOGUE:
            self.dialogue_ui.render(screen, self.dialogue)
        elif self._state == GameState.INVENTORY:
            self.inventory_ui.render(screen, self.inventory)
        elif self._state == GameState.CULTIVATION:
            self.cultivation_ui.render(screen, self.cultivation)
        elif self._state == GameState.QUEST:
            self.quest_ui.render(screen, self.quest)

    def _save_game(self, slot: int = 1):
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
        data.save(slot)

    def _load_game(self, slot: int = 1):
        data = SaveData.load(slot)
        if data:
            self.player.current_hp = data.current_hp
            self.player.max_hp = data.max_hp
            self.cultivation.current_realm_index = 0
            self.cultivation.realm_level = data.realm_level
            self.cultivation.lingli = data.lingli

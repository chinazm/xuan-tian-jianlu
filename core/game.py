"""游戏主场景：整合所有系统，运行游戏逻辑。"""
import pygame
from pathlib import Path
from core.scene_manager import Scene
from core.config import GameConfig
from core.vector import Vector2
from core.input_handler import InputHandler
from core.camera import Camera
from core.event_bus import EventBus
from core.resource_manager import ResourceManager, get_base_dir
from core.touch_controller import TouchController
from core.performance import DynamicFPS
from core.android_adapter import AndroidAdapter

ANDROID_BACK_KEY_FALLBACK = 4
ANDROID_BACK_KEY = getattr(pygame, "K_AC_BACK", ANDROID_BACK_KEY_FALLBACK)
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
        self._base_dir = Path(base_dir).resolve() if base_dir else get_base_dir()
        self._android_env = False
        self._state = GameState.PLAYING
        
        # 核心系统
        self.input = InputHandler()
        self.camera = Camera(config.window.width, config.window.height)
        self.camera.smoothing = config.render.camera_smooth
        self.resources = ResourceManager(base_path="assets", base_dir=self._base_dir)
        self.collision = CollisionSystem()
        self.combat = CombatSystem()
        self.inventory = Inventory(data_path=str(self._base_dir / "data" / "items.json"))
        self.dialogue = DialogueSystem(data_path=str(self._base_dir / "data" / "dialogues.json"))
        self.quest = QuestSystem(data_path=str(self._base_dir / "data" / "quests.json"))
        self.cultivation = CultivationSystem(data_path=str(self._base_dir / "data" / "realms.json"))
        self.particles = ParticleSystem()
        self.audio = AudioManager()
        self._audio_ready = True  # 标记音频系统是否可用
        
        # 检查 pygame.mixer 是否可用
        try:
            if not pygame.mixer.get_init():
                self._audio_ready = False
                print("[GameScene] pygame.mixer 未初始化，音频已禁用")
        except Exception:
            self._audio_ready = False
            print("[GameScene] pygame.mixer 检查失败，音频已禁用")
        
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
        self.room: Room = None
        self._room_items: list[dict] = []
        self._room_npcs: list[dict] = []
        self._awarded_quests: set[str] = set()
        self._enemy_sprites: dict[str, list] = {}
        self._npc_sprites: dict[str, list] = {}
        self.paused = False
        self.play_time = 0.0

    def on_enter(self):
        super().on_enter()
        EventBus.subscribe("entity_die", self._on_entity_die)
        EventBus.subscribe("item_pickup", self._on_item_pickup)
        EventBus.subscribe("level_up", self._on_level_up)
        self._load_room(self._room_id)
        self._check_android()

    def on_exit(self):
        EventBus.unsubscribe("entity_die", self._on_entity_die)
        EventBus.unsubscribe("item_pickup", self._on_item_pickup)
        EventBus.unsubscribe("level_up", self._on_level_up)
        if hasattr(self, "android") and self.android:
            self.android.release_wakelock()
        super().on_exit()
    
    def _check_android(self):
        """检测 Android 环境。"""
        try:
            import android
            self._android_env = True
        except ImportError:
            self._android_env = False

    def _load_room(self, room_id: str, spawn_pos: Vector2 = None):
        room_path = self._base_dir / "maps" / f"{room_id}.json"
        room = Room.from_json(str(room_path))
        if not room:
            return
        self.room = room
        self._room_id = room.room_id
        self.tilemap = Tilemap(self.resources, self._config.render.tile_size)
        self.tilemap.load(str(room_path), "tiles/tileset.png")
        self.camera.set_bounds(self.tilemap.pixel_width, self.tilemap.pixel_height)
        self.collision = CollisionSystem()
        self.collision.set_terrain(self.tilemap.get_collision_rects())
        tile_size = self._config.render.tile_size
        self._room_items = [
            {"type": item.get("type", ""), "pos": Vector2(item["pos"][0] * tile_size, item["pos"][1] * tile_size), "picked": False}
            for item in room.items if "pos" in item
        ]
        self._room_npcs = [
            {
                "id": npc.get("id", ""),
                "dialogue": npc.get("dialogue", ""),
                "pos": Vector2(npc["pos"][0] * tile_size, npc["pos"][1] * tile_size),
            }
            for npc in room.npcs if "pos" in npc
        ]
        self._npc_sprites = {}
        for npc in self._room_npcs:
            npc_id = npc["id"]
            if npc_id and npc_id not in self._npc_sprites:
                self._npc_sprites[npc_id] = self.resources.load_npc_sprite(npc_id)

        if not self.player:
            self.player = Player(pos=spawn_pos or Vector2(64, 64))
            self.player._last_reported_hp = self.player.current_hp
        else:
            self.player.pos = spawn_pos or Vector2(64, 64)
            self.player._last_reported_hp = self.player.current_hp

        self.enemies.clear()
        for e_data in room.enemies:
            pos = Vector2(e_data["pos"][0] * 32, e_data["pos"][1] * 32)
            enemy = Enemy(entity_id=f"{e_data['type']}_{len(self.enemies)}", pos=pos)
            self.enemies.append(enemy)

        for e in [self.player] + self.enemies:
            self.collision.add_entity(e)

        self.quest.start_quest("MAIN_CH01_001")
        EventBus.publish("room_enter", {"room_id": room.room_id})

        if room.music and self._audio_ready:
            self.audio.play_music(str(self._base_dir / "assets" / "music" / room.music))

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
            elif self._state == GameState.PLAYING and event.key == pygame.K_i:
                self._set_state(GameState.INVENTORY)
            elif self._state == GameState.PLAYING and event.key == pygame.K_c:
                self._set_state(GameState.CULTIVATION)
            elif self._state == GameState.PLAYING and event.key == pygame.K_q:
                self._set_state(GameState.QUEST)
            elif self._state == GameState.PLAYING and event.key == pygame.K_e:
                self._try_interact()
        
        # Android 返回键处理
        if event.type == pygame.KEYDOWN:
            if event.key == ANDROID_BACK_KEY:  # Android BACK 键
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
            selected_idx = self.inventory_ui.selected_item_index
            items = self.inventory.get_items()
            if selected_idx is not None and 0 <= selected_idx < len(items):
                item_id = items[selected_idx].item_id
                effect = self.inventory.use_item(item_id)
                self._apply_item_effect(effect)
            
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
        if self.input.consume_action("inventory"):
            self._set_state(GameState.INVENTORY)
            return
        if self.input.consume_action("cultivate"):
            self._set_state(GameState.CULTIVATION)
            return
        if self.input.consume_action("map"):
            self._set_state(GameState.QUEST)
            return
        if self.input.consume_action("interact"):
            self._try_interact()
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
        self._apply_quest_rewards()
        
        EventBus.publish("update", {"dt": dt})


    def _render_enemy_sprite(self, screen, enemy):
        """Render enemy with animated sprite sheet."""
        x = int(enemy.pos.x - self.camera.pos.x)
        y = int(enemy.pos.y - self.camera.pos.y)
        
        sprite_sheet = self._enemy_sprites.get(enemy.enemy_type)
        if not sprite_sheet:
            pygame.draw.rect(screen, (200, 50, 50), (x, y, 32, 32))
            return
        
        frame = enemy.get_sprite_frame()
        if frame < len(sprite_sheet):
            screen.blit(sprite_sheet[frame], (x, y))

    def _render_npc_sprite(self, screen, npc):
        """Render NPC with 4-direction sprite sheet (facing down, idle)."""
        x = int(npc["pos"].x - self.camera.pos.x)
        y = int(npc["pos"].y - self.camera.pos.y)
        
        sprite_sheet = self._npc_sprites.get(npc["id"])
        if not sprite_sheet:
            pygame.draw.rect(screen, (220, 190, 80), (x, y, 24, 28))
            return
        
        # Direction 0 = down, frame 0 = idle
        idx = 0  # Row 0 (down facing), col 0 (idle frame)
        if idx < len(sprite_sheet):
            screen.blit(sprite_sheet[idx], (x, y))

    def render(self, screen):
        screen.fill((20, 20, 30))
        if self.tilemap:
            self.tilemap.render(screen, self.camera)

        for enemy in self.enemies:
            if enemy.is_alive:
                self._render_enemy_sprite(screen, enemy)

        for proj in self.combat.get_projectiles():
            if proj.is_alive:
                proj.render(screen, self.camera)

        if self.player:
            self.player.render(screen, self.camera)

        for item in self._room_items:
            if item["picked"]:
                continue
            ix = int(item["pos"].x - self.camera.pos.x + 12)
            iy = int(item["pos"].y - self.camera.pos.y + 12)
            pygame.draw.circle(screen, (80, 220, 120), (ix, iy), 6)

        for npc in self._room_npcs:
            self._render_npc_sprite(screen, npc)

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
            inventory=[{"item_id": i.item_id, "quantity": i.quantity} for i in self.inventory.get_items()],
            equipment=self.inventory.get_equipment_mapping(),
            lingshi=self.inventory.lingshi,
            completed_quests=list(self.quest.completed_quests),
            play_time=self.play_time,
        )
        data.save(slot)
        EventBus.publish("game_save", {"slot": slot})

    def _load_game(self, slot: int = 1):
        data = SaveData.load(slot)
        if data:
            if data.current_room and data.current_room != self._room_id:
                self._load_room(
                    data.current_room,
                    spawn_pos=Vector2(data.player_pos[0], data.player_pos[1]),
                )
            else:
                self.player.pos = Vector2(data.player_pos[0], data.player_pos[1])

            self.player.max_hp = data.max_hp
            self.player.current_hp = max(0, min(data.current_hp, self.player.max_hp))

            target_realm = data.realm
            self.cultivation.current_realm_index = self.cultivation.find_realm_index(target_realm)
            self.cultivation.realm_level = data.realm_level
            self.cultivation.lingli = data.lingli
            self.inventory.lingshi = data.lingshi
            self.play_time = data.play_time

            self.inventory.clear_items()
            for item in data.inventory:
                self.inventory.add_item(item.get("item_id", ""), int(item.get("quantity", 1)))

            self.inventory.clear_equipment()
            for slot_name, equip_id in data.equipment.items():
                self.inventory.equip(equip_id)

            self.quest.completed_quests = list(data.completed_quests)
            self._awarded_quests = set(self.quest.completed_quests)
            EventBus.publish("game_load", {"slot": slot})

    def _apply_item_effect(self, effect: dict | None) -> None:
        if not effect:
            return
        if "hp_restore_pct" in effect:
            self.player.heal(self.player.max_hp * float(effect["hp_restore_pct"]))
        if "hp_restore" in effect:
            self.player.heal(float(effect["hp_restore"]))
        if "mp_restore_pct" in effect:
            required = self._current_realm_required_lingli()
            self.cultivation.lingli = min(required, self.cultivation.lingli + required * float(effect["mp_restore_pct"]))
        if "mp_restore" in effect:
            required = self._current_realm_required_lingli()
            self.cultivation.lingli = min(required, self.cultivation.lingli + float(effect["mp_restore"]))

    def _current_realm_required_lingli(self) -> float:
        if not self.cultivation.has_realms():
            return 100.0
        exp_list = self.cultivation.current_realm_data.get("exp_to_next", [])
        if not exp_list or self.cultivation.realm_level > len(exp_list):
            return 100.0
        return float(exp_list[self.cultivation.realm_level - 1])

    def _try_interact(self):
        if not self.player or not self.room:
            return
        tile_size = self._config.render.tile_size
        interaction_dist = tile_size * 1.5
        player_center = self.player.pos + self.player.size * 0.5

        for portal in self.room.portals:
            portal_center = Vector2(portal.pos.x * tile_size + tile_size * 0.5, portal.pos.y * tile_size + tile_size * 0.5)
            if player_center.distance_to(portal_center) <= interaction_dist:
                if Room.from_json(f"maps/{portal.target_room}.json"):
                    EventBus.publish("room_exit", {"room_id": self._room_id, "target_room": portal.target_room})
                    self._load_room(
                        portal.target_room,
                        spawn_pos=Vector2(portal.target_pos.x * tile_size, portal.target_pos.y * tile_size),
                    )
                return

        for item in self._room_items:
            if item["picked"]:
                continue
            item_center = item["pos"] + Vector2(tile_size * 0.5, tile_size * 0.5)
            if player_center.distance_to(item_center) <= interaction_dist:
                if self.inventory.add_item(item["type"], 1):
                    item["picked"] = True
                    EventBus.publish("item_pickup", {"item_id": item["type"]})
                return

        for npc in self._room_npcs:
            npc_center = npc["pos"] + Vector2(tile_size * 0.5, tile_size * 0.5)
            if player_center.distance_to(npc_center) <= interaction_dist:
                dialogue_id = npc.get("dialogue")
                if dialogue_id and self.dialogue.start(dialogue_id):
                    EventBus.publish("dialogue_start", {"dialogue_id": dialogue_id, "npc_id": npc["id"]})
                    self._set_state(GameState.DIALOGUE)
                return

    def _on_entity_die(self, data: dict):
        entity = data.get("entity")
        if not entity:
            return
        entity_id = getattr(entity, "entity_id", "")
        target_id = entity_id.rsplit("_", 1)[0] if "_" in entity_id else entity_id
        self.quest.update_from_event("entity_die", target_id)
        self._apply_quest_rewards()

    def _on_item_pickup(self, data: dict):
        target_id = data.get("item_id", "")
        if target_id:
            self.quest.update_from_event("item_pickup", target_id)
            self._apply_quest_rewards()

    def _on_level_up(self, data: dict):
        target_id = data.get("realm", "")
        if target_id:
            self.quest.update_from_event("level_up", target_id)
            self._apply_quest_rewards()

    def _apply_quest_rewards(self):
        for quest in self.quest.active_quests:
            if not quest.completed or quest.quest_id in self._awarded_quests:
                continue
            self.inventory.lingshi += quest.reward_lingshi
            for item_id in quest.reward_items:
                self.inventory.add_item(item_id, 1)
            self._awarded_quests.add(quest.quest_id)

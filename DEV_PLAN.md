# 《玄天剑录》游戏开发计划

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 开发一款像素仙侠动作冒险 RPG，核心引擎与游戏内容完全分离（外部结构架构），所有游戏数据通过 JSON 配置驱动。

**Architecture:** 
- **外部结构（External Structure）**：核心引擎代码零耦合游戏内容，引擎读取 JSON 数据 → 实例化通用实体 → 运行游戏。换一套 JSON 数据包即可变成完全不同的游戏。
- **事件总线解耦**：所有系统通过发布/订阅通信，无直接依赖。
- **组合式实体**：FSM + Animator + Collider + Stats 组件组合，拒绝继承地狱。
- **懒加载资源**：按场景预加载，LRU 缓存池，避免 Pygame 内存限制。

**Tech Stack:** Python 3.11+, Pygame 2.5+, JSON (数据配置), Python dataclass (类型安全)

**剧本依据:** `/root/xianxia_rpg_script.md`（21,600+ 字完整剧本，53个任务ID，28个场景）

---

## 外部结构架构说明

### 核心设计原则

```
┌─────────────────────────────────────────┐
│           核心引擎（不可变）              │
│  core/ - 游戏循环、输入、摄像机、事件     │
│  entities/ - 通用实体框架                │
│  systems/ - 通用系统（战斗/碰撞/背包）    │
│  world/ - 地图加载与渲染                 │
│  ui/ - 通用 UI 框架                      │
├─────────────────────────────────────────┤
│           数据层（可替换）                │
│  data/realms.json      → 境界/等级体系    │
│  data/enemies.json     → 敌人属性表       │
│  data/items.json       → 物品定义         │
│  data/equipment.json   → 装备定义         │
│  data/dialogues.json   → 对话树           │
│  data/quests.json      → 任务定义         │
│  data/scripts.json     → 剧本流程         │
│  maps/*.json           → 场景地图         │
├─────────────────────────────────────────┤
│           资源层（可替换）                │
│  assets/sprites/       → 精灵图           │
│  assets/tiles/         → Tileset         │
│  assets/audio/         → BGM/SFX         │
└─────────────────────────────────────────┘
```

### 引擎与数据的边界

| 层面 | 引擎侧（代码） | 数据侧（JSON） |
|------|---------------|---------------|
| 角色 | `Entity` 基类含位置/碰撞/状态机 | 名称、外观、初始属性 |
| 战斗 | 伤害公式、冷却管理、判定帧 | 攻击力、技能列表、伤害倍率 |
| 修炼 | 升级检测、属性计算、突破逻辑 | 境界名称、每级所需经验、解锁内容 |
| 对话 | 对话树解析、分支选择、条件判定 | 对话文本、分支条件、触发效果 |
| 地图 | Tile 渲染、摄像机、传送逻辑 | Tile 布局、传送门位置、实体初始位置 |
| 任务 | 目标追踪、条件检查、奖励发放 | 任务目标类型、完成条件、奖励内容 |

**关键规则：** 引擎代码中不出现任何游戏特定名词（如"炼气期"、"青云宗"、"御剑术"）。所有游戏特定内容必须来自 JSON 数据。

---

## Phase 1: 核心引擎基础（第1-8任务）

### Task 1: 项目初始化与目录结构

**Objective:** 创建项目骨架，建立所有目录和基础配置文件。

**Files:**
- Create: `xianxia-rpg/main.py`
- Create: `xianxia-rpg/requirements.txt`
- Create: `xianxia-rpg/config/settings.json`
- Create directories: `core/`, `entities/`, `systems/`, `world/`, `ui/`, `data/`, `maps/`, `assets/`, `tests/`

**Step 1: 创建项目结构**

```bash
mkdir -p xianxia-rpg/{core,entities,systems,world,ui,data,maps,assets/{sprites,tiles,ui,audio},tests}
cd xianxia-rpg
touch main.py requirements.txt config/settings.json
touch core/__init__.py entities/__init__.py systems/__init__.py
touch world/__init__.py ui/__init__.py tests/__init__.py
```

**Step 2: 写入 requirements.txt**

```txt
pygame>=2.5.0
```

**Step 3: 写入 config/settings.json**

```json
{
  "window": {
    "width": 800,
    "height": 600,
    "title": "玄天剑录",
    "fps": 60,
    "fullscreen": false
  },
  "render": {
    "tile_size": 32,
    "camera_smooth": 0.1
  },
  "game": {
    "default_player_name": "林凡",
    "max_save_slots": 3
  }
}
```

**Step 4: 写入 main.py**

```python
"""玄天剑录 - 像素仙侠RPG
核心引擎与游戏内容完全分离（外部结构架构）。
"""
import pygame
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

def load_settings():
    settings_path = BASE_DIR / "config" / "settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    settings = load_settings()
    win_cfg = settings["window"]
    
    pygame.init()
    screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
    pygame.display.set_caption(win_cfg["title"])
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((20, 20, 30))
        pygame.display.flip()
        clock.tick(win_cfg["fps"])
    
    pygame.quit()

if __name__ == "__main__":
    main()
```

**Step 5: 验证运行**

```bash
cd xianxia-rpg
pip install -r requirements.txt
python main.py
```
Expected: 打开 800×600 深色窗口，按 ESC 退出，无报错。

**Step 6: 提交**

```bash
git add -A && git commit -m "init: project skeleton with external structure architecture"
```

---

### Task 2: 游戏配置常量模块

**Objective:** 创建通用配置常量模块，所有魔法数字集中管理。

**Files:**
- Create: `xianxia-rpg/core/config.py`

**Step 1: 写入 config.py**

```python
"""核心配置常量。引擎默认值，可通过 config/settings.json 覆盖。"""
from dataclasses import dataclass, field

@dataclass
class WindowConfig:
    width: int = 800
    height: int = 600
    title: str = "Game"
    fps: int = 60
    fullscreen: bool = False

@dataclass
class RenderConfig:
    tile_size: int = 32
    camera_smooth: float = 0.1

@dataclass
class PhysicsConfig:
    """物理参数（通用，不绑定游戏内容）"""
    player_base_speed: float = 120.0    # 像素/秒
    player_acceleration: float = 800.0  # 加速度
    player_deceleration: float = 1000.0 # 减速度
    knockback_force: float = 80.0       # 击退力度
    knockback_duration: float = 0.15    # 击退持续时间
    dodge_distance: float = 60.0        # 闪避位移
    dodge_duration: float = 0.2         # 闪避持续时间
    dodge_cooldown: float = 0.8         # 闪避冷却

@dataclass
class CombatConfig:
    """战斗参数（通用）"""
    default_attack_cooldown: float = 0.5
    default_attack_range: float = 40.0  # 近战攻击范围（像素）
    invincibility_duration: float = 0.5 # 受击无敌时间
    i_frame_flash_speed: float = 10.0   # 无敌闪烁频率（Hz）

@dataclass 
class GameConfig:
    window: WindowConfig = field(default_factory=WindowConfig)
    render: RenderConfig = field(default_factory=RenderConfig)
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    combat: CombatConfig = field(default_factory=CombatConfig)
    
    @classmethod
    def from_json(cls, path: str) -> "GameConfig":
        """从 JSON 配置文件加载配置"""
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cfg = cls()
        if "window" in data:
            for k, v in data["window"].items():
                if hasattr(cfg.window, k):
                    setattr(cfg.window, k, v)
        if "render" in data:
            for k, v in data["render"].items():
                if hasattr(cfg.render, k):
                    setattr(cfg.render, k, v)
        return cfg
```

**Step 2: 写入测试**

```bash
mkdir -p tests/core
cat > tests/core/test_config.py << 'EOF'
"""测试配置加载"""
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import GameConfig, WindowConfig

def test_default_config():
    cfg = GameConfig()
    assert cfg.window.width == 800
    assert cfg.window.fps == 60
    assert cfg.render.tile_size == 32
    assert cfg.physics.player_base_speed == 120.0
    assert cfg.combat.default_attack_cooldown == 0.5

def test_load_from_json():
    data = {
        "window": {"width": 1024, "height": 768, "title": "Test"},
        "render": {"tile_size": 16}
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        cfg = GameConfig.from_json(f.name)
    
    assert cfg.window.width == 1024
    assert cfg.window.height == 768
    assert cfg.window.title == "Test"
    assert cfg.render.tile_size == 16
    # 未设置的字段保持默认值
    assert cfg.window.fps == 60

if __name__ == "__main__":
    test_default_config()
    test_load_from_json()
    print("All config tests passed!")
EOF
```

**Step 3: 运行测试**

```bash
cd xianxia-rpg
python tests/core/test_config.py
```
Expected: `All config tests passed!`

**Step 4: 提交**

```bash
git add -A && git commit -m "feat: add core config module with dataclass defaults and JSON override"
```

---

### Task 3: 输入处理系统

**Objective:** 实现键盘输入处理，支持方向键实时响应 + 动作键输入缓冲。

**Files:**
- Create: `xianxia-rpg/core/input_handler.py`
- Create: `tests/core/test_input_handler.py`

**Step 1: 写入测试**

```python
# tests/core/test_input_handler.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input_handler import InputHandler

class MockKeyState:
    def __init__(self, pressed_keys=None):
        self._pressed = set(pressed_keys or [])
    
    def get_pressed(self):
        import pygame
        result = [False] * 300
        for k in self._pressed:
            result[k] = True
        return result

def test_directional_input():
    handler = InputHandler()
    # 模拟按下 W 和 D
    handler._mock_get_pressed = MockKeyState([87, 68]).get_pressed  # W=87, D=68
    handler.update(0.016)
    
    # 方向向量应为右上 (1, -1) 归一化后
    assert handler.direction.x > 0
    assert handler.direction.y < 0

def test_action_buffer():
    handler = InputHandler()
    handler._key_just_pressed = {"attack": True}
    handler.update(0.016)
    
    assert handler.consume_action("attack") == True
    assert handler.consume_action("attack") == False  # 已消费

def test_no_buffer_without_press():
    handler = InputHandler()
    handler._key_just_pressed = {}
    handler.update(0.016)
    assert handler.consume_action("attack") == False

if __name__ == "__main__":
    test_directional_input()
    test_action_buffer()
    test_no_buffer_without_press()
    print("All input tests passed!")
```

**Step 2: 写入实现**

```python
# core/input_handler.py
"""输入处理系统：方向键实时响应 + 动作键缓冲队列。"""
from dataclasses import dataclass, field
from typing import Optional
import pygame
from .vector import Vector2

# 默认键位映射（可通过配置覆盖）
DEFAULT_KEY_MAP = {
    pygame.K_w: "up",
    pygame.K_s: "down",
    pygame.K_a: "left",
    pygame.K_d: "right",
    pygame.K_j: "attack",
    pygame.K_k: "skill",
    pygame.K_l: "dodge",
    pygame.K_e: "interact",
    pygame.K_i: "inventory",
    pygame.K_c: "cultivate",
    pygame.K_r: "realm",
    pygame.K_m: "map",
    pygame.K_ESCAPE: "menu",
}

@dataclass
class InputHandler:
    key_map: dict = field(default_factory=lambda: dict(DEFAULT_KEY_MAP))
    direction: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    action_buffer: list = field(default_factory=list)
    buffer_max: int = 5
    
    # 内部状态
    _prev_key_state: set = field(default_factory=set, repr=False)
    _key_just_pressed: dict = field(default_factory=dict, repr=False)
    
    def update(self, dt: float):
        """每帧更新输入状态。"""
        keys = pygame.key.get_pressed()
        current_pressed = set()
        
        # 更新方向输入
        dx, dy = 0, 0
        for keycode, action in self.key_map.items():
            is_down = keys[keycode]
            if is_down:
                current_pressed.add(keycode)
            
            if action in ("up", "down", "left", "right"):
                if is_down:
                    if action == "up": dy = -1
                    elif action == "down": dy = 1
                    elif action == "left": dx = -1
                    elif action == "right": dx = 1
        
        # 归一化对角线移动
        if dx != 0 and dy != 0:
            length = (dx*dx + dy*dy) ** 0.5
            dx /= length
            dy /= length
        
        self.direction = Vector2(dx, dy)
        
        # 检测新按下的动作键
        self._key_just_pressed.clear()
        for keycode, action in self.key_map.items():
            if action not in ("up", "down", "left", "right"):
                was_down = keycode in self._prev_key_state
                is_down = keys[keycode]
                if is_down and not was_down:
                    self._key_just_pressed[action] = True
                    if len(self.action_buffer) < self.buffer_max:
                        self.action_buffer.append(action)
        
        self._prev_key_state = current_pressed
    
    def consume_action(self, action_name: str) -> bool:
        """从缓冲中消费一个动作。返回 True 如果成功消费。"""
        if action_name in self.action_buffer:
            self.action_buffer.remove(action_name)
            return True
        return False
    
    def is_action_just_pressed(self, action_name: str) -> bool:
        """检查动作键是否在本帧刚按下（不消费）。"""
        return self._key_just_pressed.get(action_name, False)
    
    def is_direction_held(self) -> bool:
        """检查是否有方向键被按住。"""
        return self.direction.length() > 0
```

**Step 3: 创建 Vector2 工具类**

```python
# core/vector.py
"""轻量级 2D 向量，避免引入 numpy 依赖。"""
import math
from dataclasses import dataclass

@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalized(self):
        l = self.length()
        if l == 0:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)
    
    def distance_to(self, other):
        return (self - other).length()
    
    def tuple(self):
        return (self.x, self.y)
```

**Step 4: 运行测试**

```bash
cd xianxia-rpg
python tests/core/test_input_handler.py
```
Expected: `All input tests passed!`

**Step 5: 提交**

```bash
git add -A && git commit -m "feat: add input handler with directional input + action buffer"
```

---

### Task 4: 事件总线系统

**Objective:** 实现发布/订阅事件总线，解耦各系统间通信。

**Files:**
- Create: `xianxia-rpg/core/event_bus.py`
- Create: `tests/core/test_event_bus.py`

**Step 1: 写入测试**

```python
# tests/core/test_event_bus.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.event_bus import EventBus

def test_subscribe_and_publish():
    EventBus.clear()
    results = []
    
    def handler(data):
        results.append(data)
    
    EventBus.subscribe("entity_hit", handler)
    EventBus.publish("entity_hit", {"damage": 10})
    
    assert len(results) == 1
    assert results[0]["damage"] == 10

def test_multiple_subscribers():
    EventBus.clear()
    results_a = []
    results_b = []
    
    EventBus.subscribe("level_up", lambda d: results_a.append(d))
    EventBus.subscribe("level_up", lambda d: results_b.append(d))
    
    EventBus.publish("level_up", {"level": 2})
    
    assert len(results_a) == 1
    assert len(results_b) == 1

def test_unsubscribe():
    EventBus.clear()
    results = []
    handler = lambda d: results.append(d)
    
    EventBus.subscribe("test", handler)
    EventBus.unsubscribe("test", handler)
    EventBus.publish("test", {})
    
    assert len(results) == 0

def test_no_subscribers_does_not_crash():
    EventBus.clear()
    EventBus.publish("nonexistent_event", {"data": 123})  # Should not raise

if __name__ == "__main__":
    test_subscribe_and_publish()
    test_multiple_subscribers()
    test_unsubscribe()
    test_no_subscribers_does_not_crash()
    print("All event bus tests passed!")
```

**Step 2: 写入实现**

```python
# core/event_bus.py
"""事件总线：发布/订阅模式，解耦系统间通信。"""
from typing import Callable
from collections import defaultdict

class EventBus:
    _subscribers: dict[str, list[Callable]] = defaultdict(list)
    
    @classmethod
    def subscribe(cls, event_name: str, callback: Callable):
        """订阅事件。"""
        cls._subscribers[event_name].append(callback)
    
    @classmethod
    def unsubscribe(cls, event_name: str, callback: Callable):
        """取消订阅。"""
        if event_name in cls._subscribers:
            cls._subscribers[event_name].remove(callback)
    
    @classmethod
    def publish(cls, event_name: str, data: dict = None):
        """发布事件，通知所有订阅者。"""
        for cb in cls._subscribers.get(event_name, []):
            cb(data or {})
    
    @classmethod
    def clear(cls):
        """清除所有订阅（用于测试）。"""
        cls._subscribers.clear()

# --- 预定义事件（引擎层） ---
# 这些是事件名称约定，不是硬编码的游戏逻辑。
# 任何系统都可以发布和订阅这些事件。

ENTITY_EVENTS = [
    "entity_spawn",      # 实体生成
    "entity_hit",        # 实体受击
    "entity_die",        # 实体死亡
    "item_pickup",       # 拾取物品
]

PROGRESSION_EVENTS = [
    "stat_change",       # 属性变化
    "level_up",          # 等级/境界提升
    "breakthrough_fail", # 突破失败
    "quest_start",       # 任务开始
    "quest_complete",    # 任务完成
    "objective_update",  # 任务目标更新
]

GAME_EVENTS = [
    "room_enter",        # 进入新场景
    "room_exit",         # 离开场景
    "dialogue_start",    # 对话开始
    "dialogue_end",      # 对话结束
    "game_pause",        # 游戏暂停
    "game_save",         # 存档
    "game_load",         # 读档
]
```

**Step 3: 运行测试**

```bash
cd xianxia-rpg
python tests/core/test_event_bus.py
```
Expected: `All event bus tests passed!`

**Step 4: 提交**

```bash
git add -A && git commit -m "feat: add event bus with pub/sub and predefined event constants"
```

---

### Task 5: 资源懒加载管理器

**Objective:** 实现带 LRU 淘汰的懒加载资源管理器，避免预加载所有资源导致内存溢出。

**Files:**
- Create: `xianxia-rpg/core/resource_manager.py`
- Create: `tests/core/test_resource_manager.py`

**Step 1: 写入实现**

```python
# core/resource_manager.py
"""资源懒加载管理器：LRU 缓存 + 按需加载。"""
import pygame
from pathlib import Path
from collections import OrderedDict
from typing import Optional

class ResourceManager:
    def __init__(self, max_cache_size: int = 100, base_path: str = "assets"):
        self._cache: OrderedDict[str, pygame.Surface] = OrderedDict()
        self._max_size = max_cache_size
        self._base_path = Path(base_path)
    
    def load(self, relative_path: str) -> pygame.Surface:
        """加载图片（懒加载 + LRU 缓存）。"""
        if relative_path in self._cache:
            # 命中缓存，移到末尾（最近使用）
            self._cache.move_to_end(relative_path)
            return self._cache[relative_path]
        
        # 未命中，加载
        full_path = self._base_path / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Resource not found: {full_path}")
        
        surface = pygame.image.load(str(full_path)).convert_alpha()
        
        # LRU 淘汰
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # 删除最久未使用的
        
        self._cache[relative_path] = surface
        return surface
    
    def load_spritesheet(
        self, relative_path: str, tile_w: int = 32, tile_h: int = 32
    ) -> list[pygame.Surface]:
        """加载精灵表并切分为帧列表。"""
        sheet = self.load(relative_path)
        frames = []
        cols = sheet.get_width() // tile_w
        rows = sheet.get_height() // tile_h
        
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * tile_w, row * tile_h, tile_w, tile_h)
                frames.append(sheet.subsurface(rect))
        
        return frames
    
    def preload_paths(self, paths: list[str]):
        """预加载指定路径的资源（用于场景切换前预加载）。"""
        for path in paths:
            try:
                self.load(path)
            except FileNotFoundError:
                pass  # 记录日志但不中断
    
    def cache_info(self) -> dict:
        return {
            "cached": len(self._cache),
            "max_size": self._max_size,
        }
    
    def clear(self):
        """清空缓存。"""
        self._cache.clear()
```

**Step 2: 写入测试**

```python
# tests/core/test_resource_manager.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from core.resource_manager import ResourceManager

def test_cache_lru_eviction():
    """测试 LRU 淘汰机制"""
    pygame.init()
    
    # 创建测试图片
    test_dir = Path("tests/test_assets")
    test_dir.mkdir(exist_ok=True)
    for i in range(5):
        surf = pygame.Surface((16, 16))
        surf.fill((255, 0, 0))
        pygame.image.save(surf, str(test_dir / f"test_{i}.png"))
    
    mgr = ResourceManager(max_cache_size=3, base_path="tests/test_assets")
    
    # 加载 5 张图片，但缓存只能存 3 张
    for i in range(5):
        mgr.load(f"test_{i}.png")
    
    info = mgr.cache_info()
    assert info["cached"] == 3  # 只有最后 3 张在缓存中
    
    # 清理
    for i in range(5):
        (test_dir / f"test_{i}.png").unlink(missing_ok=True)
    test_dir.rmdir()
    
    pygame.quit()
    print("LRU eviction test passed!")

def test_spritesheet_split():
    """测试精灵表切分"""
    pygame.init()
    
    test_dir = Path("tests/test_assets")
    test_dir.mkdir(exist_ok=True)
    
    # 创建 64x32 的精灵表（2帧，每帧32x32）
    sheet = pygame.Surface((64, 32))
    sheet.fill((255, 0, 0))
    subsurf = sheet.subsurface((32, 0, 32, 32))
    subsurf.fill((0, 255, 0))
    pygame.image.save(sheet, str(test_dir / "test_sheet.png"))
    
    mgr = ResourceManager(max_cache_size=10, base_path="tests/test_assets")
    frames = mgr.load_spritesheet("test_sheet.png", tile_w=32, tile_h=32)
    
    assert len(frames) == 2
    
    # 清理
    (test_dir / "test_sheet.png").unlink()
    test_dir.rmdir()
    
    pygame.quit()
    print("Spritesheet split test passed!")

if __name__ == "__main__":
    test_cache_lru_eviction()
    test_spritesheet_split()
    print("All resource manager tests passed!")
```

**Step 3: 运行测试**

```bash
cd xianxia-rpg
python tests/core/test_resource_manager.py
```

**Step 4: 提交**

```bash
git add -A && git commit -m "feat: add resource manager with LRU cache and spritesheet support"
```

---

### Task 6: 摄像机系统

**Objective:** 实现平滑跟随摄像机，支持地图边界限制。

**Files:**
- Create: `xianxia-rpg/core/camera.py`
- Create: `tests/core/test_camera.py`

**Step 1: 写入实现**

```python
# core/camera.py
"""摄像机系统：平滑跟随目标，限制在地图边界内。"""
from .vector import Vector2

class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pos = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.smoothing = 0.1  # 平滑系数（0-1）
        self.map_bounds = None  # (width, height) 或 None（无限制）
    
    def set_bounds(self, map_width: int, map_height: int):
        """设置地图边界，摄像机不会超出。"""
        self.map_bounds = (map_width, map_height)
    
    def follow(self, target_pos: Vector2, dt: float):
        """每帧跟随目标位置。"""
        self.target = Vector2(
            target_pos.x - self.width // 2,
            target_pos.y - self.height // 2
        )
        
        # 平滑插值
        self.pos.x += (self.target.x - self.pos.x) * self.smoothing
        self.pos.y += (self.target.y - self.pos.y) * self.smoothing
        
        # 限制在地图边界内
        if self.map_bounds:
            mw, mh = self.map_bounds
            self.pos.x = max(0, min(self.pos.x, mw - self.width))
            self.pos.y = max(0, min(self.pos.y, mh - self.height))
    
    def apply(self, pos: Vector2) -> Vector2:
        """将世界坐标转换为屏幕坐标。"""
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y)
    
    def is_visible(self, pos: Vector2, size: Vector2, margin: int = 64) -> bool:
        """检查物体是否在视口内（含缓冲区）。"""
        screen_pos = self.apply(pos)
        return not (
            screen_pos.x + size.x < -margin or
            screen_pos.x > self.width + margin or
            screen_pos.y + size.y < -margin or
            screen_pos.y > self.height + margin
        )
    
    def world_rect(self) -> tuple:
        """返回当前视口对应的世界坐标区域。"""
        return (
            int(self.pos.x),
            int(self.pos.y),
            int(self.pos.x + self.width),
            int(self.pos.y + self.height)
        )
```

**Step 2: 写入测试**

```python
# tests/core/test_camera.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.camera import Camera
from core.vector import Vector2

def test_camera_follow():
    cam = Camera(800, 600)
    target = Vector2(400, 300)
    cam.follow(target, 0.016)
    
    # 摄像机应跟随到目标附近
    assert abs(cam.pos.x - (400 - 400)) < 1
    assert abs(cam.pos.y - (300 - 300)) < 1

def test_camera_bounds():
    cam = Camera(800, 600)
    cam.set_bounds(1600, 1200)
    
    # 目标在地图右下角
    target = Vector2(1500, 1100)
    for _ in range(100):
        cam.follow(target, 0.016)
    
    # 摄像机不应超出地图边界
    assert cam.pos.x >= 0
    assert cam.pos.y >= 0
    assert cam.pos.x + cam.width <= 1600
    assert cam.pos.y + cam.height <= 1200

def test_world_to_screen():
    cam = Camera(800, 600)
    cam.pos = Vector2(100, 50)
    
    world_pos = Vector2(200, 150)
    screen_pos = cam.apply(world_pos)
    
    assert screen_pos.x == 100  # 200 - 100
    assert screen_pos.y == 100  # 150 - 50

def test_visibility_check():
    cam = Camera(800, 600)
    cam.pos = Vector2(0, 0)
    
    # 在视口内
    assert cam.is_visible(Vector2(100, 100), Vector2(32, 32))
    # 在视口外（左边）
    assert not cam.is_visible(Vector2(-100, 100), Vector2(32, 32))
    # 在视口外（右边）
    assert not cam.is_visible(Vector2(900, 100), Vector2(32, 32))

if __name__ == "__main__":
    test_camera_follow()
    test_camera_bounds()
    test_world_to_screen()
    test_visibility_check()
    print("All camera tests passed!")
```

**Step 3: 运行测试**

```bash
cd xianxia-rpg
python tests/core/test_camera.py
```

**Step 4: 提交**

```bash
git add -A && git commit -m "feat: add camera system with smooth follow and map bounds"
```

---

### Task 7: 日志系统

**Objective:** 实现分级日志系统，支持控制台输出和文件写入。

**Files:**
- Create: `xianxia-rpg/core/logger.py`

**Step 1: 写入实现**

```python
# core/logger.py
"""分级日志系统。"""
import logging
from pathlib import Path
from datetime import datetime

class GameLogger:
    _instance = None
    
    @classmethod
    def get(cls, name: str = "game") -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls._setup(name)
        return cls._instance
    
    @staticmethod
    def _setup(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 控制台输出
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        # 文件输出
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            log_dir / f"{name}_{timestamp}.log", encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console)
        logger.addHandler(file_handler)
        
        return logger
```

**Step 2: 验证**

```bash
cd xianxia-rpg
python -c "
from core.logger import GameLogger
log = GameLogger.get()
log.info('Logger initialized')
log.debug('Debug message (file only)')
log.warning('Warning test')
import os
print('Log files:', os.listdir('logs'))
"
```

Expected: 控制台显示 INFO 和 WARNING，logs/ 目录下生成日志文件。

**Step 3: 提交**

```bash
git add -A && git commit -m "feat: add logging system with console + file output"
```

---

### Task 8: 场景管理器

**Objective:** 实现场景切换系统，支持淡入淡出过渡效果。

**Files:**
- Create: `xianxia-rpg/core/scene_manager.py`

**Step 1: 写入实现**

```python
# core/scene_manager.py
"""场景管理器：场景切换 + 淡入淡出过渡。"""
import pygame
from typing import Optional, Callable
from .logger import GameLogger

logger = GameLogger.get("scene")

class Scene:
    """场景基类。每个场景实现自己的 update 和 render。"""
    def __init__(self, name: str):
        self.name = name
    
    def on_enter(self):
        """进入场景时调用。"""
        logger.info(f"Entering scene: {self.name}")
    
    def on_exit(self):
        """离开场景时调用。"""
        logger.info(f"Exiting scene: {self.name}")
    
    def handle_event(self, event: pygame.event.Event):
        """处理单个事件。"""
        pass
    
    def update(self, dt: float):
        """更新场景逻辑。"""
        pass
    
    def render(self, screen: pygame.Surface):
        """渲染场景。"""
        pass


class SceneManager:
    def __init__(self):
        self._scenes: dict[str, Scene] = {}
        self._current: Optional[Scene] = None
        self._transition = None  # 切换过渡效果
    
    def register(self, scene: Scene):
        """注册场景。"""
        self._scenes[scene.name] = scene
    
    def switch_to(self, scene_name: str, fade_duration: float = 0.5):
        """切换到指定场景（带淡入淡出）。"""
        if scene_name not in self._scenes:
            logger.error(f"Scene not found: {scene_name}")
            return
        
        self._transition = {
            "phase": "fade_out",
            "alpha": 0.0,
            "duration": fade_duration,
            "elapsed": 0.0,
            "next_scene": scene_name,
        }
    
    def set_immediate(self, scene_name: str):
        """立即切换场景（无过渡）。"""
        if self._current:
            self._current.on_exit()
        self._current = self._scenes[scene_name]
        self._current.on_enter()
    
    def update(self, dt: float):
        """更新当前场景和过渡效果。"""
        if self._transition:
            self._transition["elapsed"] += dt
            progress = self._transition["elapsed"] / self._transition["duration"]
            
            if self._transition["phase"] == "fade_out":
                self._transition["alpha"] = min(1.0, progress)
                if progress >= 1.0:
                    # 切换场景
                    next_name = self._transition["next_scene"]
                    if self._current:
                        self._current.on_exit()
                    self._current = self._scenes[next_name]
                    self._current.on_enter()
                    self._transition["phase"] = "fade_in"
                    self._transition["elapsed"] = 0.0
            
            elif self._transition["phase"] == "fade_in":
                self._transition["alpha"] = max(0.0, 1.0 - progress)
                if progress >= 1.0:
                    self._transition = None
            
            # 过渡期间也更新场景逻辑
            if self._current:
                self._current.update(dt)
        else:
            if self._current:
                self._current.update(dt)
    
    def render(self, screen: pygame.Surface):
        """渲染当前场景和过渡效果。"""
        if self._current:
            self._current.render(screen)
        
        if self._transition:
            alpha = int(self._transition["alpha"] * 255)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))
    
    def handle_event(self, event: pygame.event.Event):
        """传递事件到当前场景。"""
        if self._current:
            self._current.handle_event(event)
    
    @property
    def current_scene_name(self) -> Optional[str]:
        return self._current.name if self._current else None
```

**Step 2: 提交**

```bash
git add -A && git commit -m "feat: add scene manager with fade transitions"
```

---

## Phase 2: 实体框架（第9-14任务）

### Task 9: 实体基类（Entity）

**Objective:** 创建通用实体基类，支持位置、碰撞框、速度、渲染。

**Files:**
- Create: `xianxia-rpg/entities/entity.py`
- Create: `tests/entities/test_entity.py`

**Step 1: 写入实现**

```python
# entities/entity.py
"""通用实体基类。不绑定任何游戏内容，纯数据驱动。"""
from dataclasses import dataclass, field
from typing import Optional
import pygame
from core.vector import Vector2
from core.event_bus import EventBus

@dataclass
class Entity:
    entity_id: str                              # 唯一标识（来自 JSON）
    pos: Vector2                                # 世界坐标
    size: Vector2 = field(default_factory=lambda: Vector2(32, 32))
    vel: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    facing: str = "down"                        # 朝向: up/down/left/right
    
    # 属性（通用数值，具体含义由 JSON 定义）
    max_hp: float = 100.0
    current_hp: float = 100.0
    base_speed: float = 100.0                   # 基础移动速度（像素/秒）
    
    # 渲染
    sprite: Optional[pygame.Surface] = None
    animation_frames: list = field(default_factory=list)
    current_frame: int = 0
    frame_timer: float = 0.0
    frame_duration: float = 0.15                # 每帧持续时间（秒）
    
    # 状态
    is_alive: bool = True
    is_knockback: bool = False
    knockback_timer: float = 0.0
    
    def update(self, dt: float):
        """更新实体状态。"""
        if not self.is_alive:
            return
        
        # 击退处理
        if self.is_knockback:
            self.knockback_timer -= dt
            if self.knockback_timer <= 0:
                self.is_knockback = False
                self.vel = Vector2(0, 0)
        
        # 移动
        self.pos = self.pos + self.vel * dt
    
    def take_damage(self, amount: float, source_pos: Vector2, knockback_force: float = 80.0):
        """受击：扣血 + 击退。"""
        self.current_hp = max(0, self.current_hp - amount)
        
        # 击退
        direction = (self.pos - source_pos).normalized()
        if direction.length() == 0:
            direction = Vector2(0, -1)  # 默认向上
        self.vel = direction * knockback_force
        self.is_knockback = True
        self.knockback_timer = 0.15
        
        # 发布事件
        EventBus.publish("entity_hit", {
            "entity": self,
            "damage": amount,
            "source_pos": source_pos,
        })
        
        if self.current_hp <= 0:
            self.is_alive = False
            EventBus.publish("entity_die", {
                "entity": self,
                "killer_pos": source_pos,
            })
    
    def heal(self, amount: float):
        """恢复生命值。"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def get_collision_rect(self) -> pygame.Rect:
        """获取碰撞矩形。"""
        return pygame.Rect(
            int(self.pos.x),
            int(self.pos.y),
            int(self.size.x),
            int(self.size.y),
        )
    
    def render(self, screen: pygame.Surface, camera) -> None:
        """渲染实体（自动处理摄像机偏移）。"""
        if not self.sprite:
            return
        
        screen_pos = camera.apply(self.pos)
        
        # 如果不在视口内，跳过渲染
        if not camera.is_visible(self.pos, self.size):
            return
        
        screen.blit(self.sprite, (int(screen_pos.x), int(screen_pos.y)))
    
    def animate(self, dt: float):
        """更新动画帧。"""
        if len(self.animation_frames) <= 1:
            return
        
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.sprite = self.animation_frames[self.current_frame]
```

**Step 2: 写入测试**

```python
# tests/entities/test_entity.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from entities.entity import Entity
from core.vector import Vector2
from core.event_bus import EventBus

def test_entity_creation():
    e = Entity(entity_id="test_001", pos=Vector2(100, 200))
    assert e.entity_id == "test_001"
    assert e.pos.x == 100
    assert e.pos.y == 200
    assert e.is_alive

def test_take_damage():
    EventBus.clear()
    e = Entity(entity_id="test", pos=Vector2(0, 0), max_hp=100, current_hp=100)
    e.take_damage(30, Vector2(0, 50))
    assert e.current_hp == 70
    assert e.is_knockback

def test_death():
    EventBus.clear()
    e = Entity(entity_id="test", pos=Vector2(0, 0), max_hp=50, current_hp=50)
    e.take_damage(50, Vector2(0, 50))
    assert e.current_hp == 0
    assert not e.is_alive

def test_heal():
    e = Entity(entity_id="test", pos=Vector2(0, 0), max_hp=100, current_hp=50)
    e.heal(30)
    assert e.current_hp == 80
    # 不超过上限
    e.heal(50)
    assert e.current_hp == 100

def test_collision_rect():
    e = Entity(entity_id="test", pos=Vector2(100, 200), size=Vector2(32, 32))
    rect = e.get_collision_rect()
    assert rect.x == 100
    assert rect.y == 200
    assert rect.width == 32
    assert rect.height == 32

if __name__ == "__main__":
    test_entity_creation()
    test_take_damage()
    test_death()
    test_heal()
    test_collision_rect()
    print("All entity tests passed!")
```

**Step 3: 运行测试**

```bash
cd xianxia-rpg
python tests/entities/test_entity.py
```

**Step 4: 提交**

```bash
git add -A && git commit -m "feat: add Entity base class with HP, knockback, animation, and collision"
```

---

### Task 10: 状态机组（FSM）

**Objective:** 实现轻量级有限状态机，支持状态切换和生命周期回调。

**Files:**
- Create: `xianxia-rpg/entities/fsm.py`
- Create: `tests/entities/test_fsm.py`

**Step 1: 写入实现**

```python
# entities/fsm.py
"""轻量级有限状态机。"""
from typing import Callable, Optional, Any

class State:
    def __init__(
        self, name: str,
        on_enter: Optional[Callable] = None,
        on_update: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
    ):
        self.name = name
        self.on_enter = on_enter
        self.on_update = on_update
        self.on_exit = on_exit

class FSM:
    def __init__(self):
        self._states: dict[str, State] = {}
        self._current: Optional[State] = None
        self._params: dict[str, Any] = {}
    
    def add_state(self, state: State):
        self._states[state.name] = state
    
    def set_state(self, name: str, params: dict = None):
        """切换到指定状态。"""
        if name not in self._states:
            raise ValueError(f"State not found: {name}")
        
        if self._current:
            if self._current.on_exit:
                self._current.on_exit()
        
        self._current = self._states[name]
        self._params = params or {}
        
        if self._current.on_enter:
            self._current.on_enter(self._params)
    
    def update(self, dt: float):
        if self._current and self._current.on_update:
            self._current.on_update(dt, self._params)
    
    @property
    def current_state(self) -> Optional[str]:
        return self._current.name if self._current else None
```

**Step 2: 写入测试**

```python
# tests/entities/test_fsm.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from entities.fsm import FSM, State

def test_state_transitions():
    fsm = FSM()
    transitions = []
    
    fsm.add_state(State("idle", 
        on_enter=lambda p: transitions.append("enter_idle"),
        on_exit=lambda: transitions.append("exit_idle")
    ))
    fsm.add_state(State("walk",
        on_enter=lambda p: transitions.append(f"enter_walk_{p.get('dir', '')}")
    ))
    
    fsm.set_state("idle")
    assert fsm.current_state == "idle"
    assert transitions == ["enter_idle"]
    
    fsm.set_state("walk", {"dir": "right"})
    assert fsm.current_state == "walk"
    assert transitions == ["enter_idle", "exit_idle", "enter_walk_right"]

def test_state_update():
    fsm = FSM()
    update_count = [0]
    
    def update_handler(dt, params):
        update_count[0] += 1
    
    fsm.add_state(State("move", on_update=update_handler))
    fsm.set_state("move")
    
    fsm.update(0.016)
    fsm.update(0.016)
    assert update_count[0] == 2

def test_invalid_state_raises():
    fsm = FSM()
    fsm.add_state(State("valid"))
    try:
        fsm.set_state("nonexistent")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

if __name__ == "__main__":
    test_state_transitions()
    test_state_update()
    test_invalid_state_raises()
    print("All FSM tests passed!")
```

**Step 3: 运行测试并提交**

```bash
cd xianxia-rpg
python tests/entities/test_fsm.py
git add -A && git commit -m "feat: add FSM state machine with lifecycle callbacks"
```

---

### Task 11: 碰撞检测系统

**Objective:** 实现 AABB 碰撞检测 + 碰撞层系统，区分不同实体类型。

**Files:**
- Create: `xianxia-rpg/systems/collision.py`
- Create: `tests/systems/test_collision.py`

**Step 1: 写入实现**

```python
# systems/collision.py
"""AABB 碰撞检测 + 碰撞层系统。"""
import pygame
from typing import Optional
from core.vector import Vector2
from entities.entity import Entity

# 碰撞层定义（通用，不绑定游戏内容）
COLLISION_LAYER = {
    "TERRAIN": 1,      # 地形/墙壁（不可穿越）
    "ENTITY": 2,       # 实体（玩家、敌人、NPC）
    "PROJECTILE": 4,   # 投射物
    "TRIGGER": 8,      # 触发器（不可见，用于事件）
}

class CollisionSystem:
    def __init__(self):
        self._terrain_rects: list[pygame.Rect] = []
        self._entities: dict[str, Entity] = {}
    
    def set_terrain(self, rects: list[pygame.Rect]):
        """设置地形碰撞区域。"""
        self._terrain_rects = rects
    
    def add_entity(self, entity: Entity):
        """注册实体用于碰撞检测。"""
        self._entities[entity.entity_id] = entity
    
    def remove_entity(self, entity_id: str):
        self._entities.pop(entity_id, None)
    
    def check_terrain_collision(self, rect: pygame.Rect) -> bool:
        """检查是否与地形碰撞。"""
        for terrain_rect in self._terrain_rects:
            if rect.colliderect(terrain_rect):
                return True
        return False
    
    def resolve_terrain(self, entity: Entity) -> Vector2:
        """解决地形碰撞：推回未重叠的方向。"""
        rect = entity.get_collision_rect()
        
        for terrain_rect in self._terrain_rects:
            if not rect.colliderect(terrain_rect):
                continue
            
            # 计算重叠量
            overlap_x = min(rect.right - terrain_rect.left, terrain_rect.right - rect.left)
            overlap_y = min(rect.bottom - terrain_rect.top, terrain_rect.bottom - rect.top)
            
            # 沿最小重叠方向推回
            if overlap_x < overlap_y:
                if rect.centerx < terrain_rect.centerx:
                    entity.pos.x -= overlap_x
                else:
                    entity.pos.x += overlap_x
            else:
                if rect.centery < terrain_rect.centery:
                    entity.pos.y -= overlap_y
                else:
                    entity.pos.y += overlap_y
        
        return entity.pos
    
    def check_entity_collision(self, a: Entity, b: Entity) -> bool:
        """检查两个实体是否碰撞。"""
        return a.get_collision_rect().colliderect(b.get_collision_rect())
    
    def get_nearby_entities(self, pos: Vector2, radius: float) -> list[Entity]:
        """获取指定半径内的所有实体。"""
        result = []
        radius_sq = radius * radius
        for entity in self._entities.values():
            if not entity.is_alive:
                continue
            dist_sq = (entity.pos - pos).length() ** 2
            if dist_sq <= radius_sq:
                result.append(entity)
        return result
    
    def get_entities_in_rect(self, rect: pygame.Rect) -> list[Entity]:
        """获取在指定矩形内的所有实体。"""
        result = []
        for entity in self._entities.values():
            if not entity.is_alive:
                continue
            if entity.get_collision_rect().colliderect(rect):
                result.append(entity)
        return result
```

**Step 2: 写入测试**

```python
# tests/systems/test_collision.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pygame
from systems.collision import CollisionSystem
from entities.entity import Entity
from core.vector import Vector2

def test_terrain_collision():
    cs = CollisionSystem()
    cs.set_terrain([pygame.Rect(100, 100, 100, 100)])
    
    # 不相交
    assert not cs.check_terrain_collision(pygame.Rect(0, 0, 32, 32))
    # 相交
    assert cs.check_terrain_collision(pygame.Rect(110, 110, 32, 32))

def test_entity_collision():
    cs = CollisionSystem()
    a = Entity(entity_id="a", pos=Vector2(0, 0), size=Vector2(32, 32))
    b = Entity(entity_id="b", pos=Vector2(20, 20), size=Vector2(32, 32))
    
    assert cs.check_entity_collision(a, b)
    
    b.pos = Vector2(100, 100)
    assert not cs.check_entity_collision(a, b)

def test_nearby_entities():
    cs = CollisionSystem()
    e1 = Entity(entity_id="e1", pos=Vector2(0, 0))
    e2 = Entity(entity_id="e2", pos=Vector2(50, 0))
    e3 = Entity(entity_id="e3", pos=Vector2(200, 0))
    
    cs.add_entity(e1)
    cs.add_entity(e2)
    cs.add_entity(e3)
    
    nearby = cs.get_nearby_entities(Vector2(0, 0), radius=100)
    assert len(nearby) == 2  # e1 and e2, not e3

if __name__ == "__main__":
    test_terrain_collision()
    test_entity_collision()
    test_nearby_entities()
    print("All collision tests passed!")
```

**Step 3: 运行测试并提交**

```bash
cd xianxia-rpg
python tests/systems/test_collision.py
git add -A && git commit -m "feat: add collision system with AABB + terrain resolution"
```

---

### Task 12: 动画控制器

**Objective:** 实现动画控制器，管理精灵帧播放。

**Files:**
- Create: `xianxia-rpg/entities/animator.py`

**Step 1: 写入实现**

```python
# entities/animator.py
"""动画控制器：管理精灵帧序列播放。"""
import pygame
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Animation:
    name: str
    frames: list[pygame.Surface]
    frame_duration: float = 0.15
    loop: bool = True
    on_complete: Optional[callable] = None

class Animator:
    def __init__(self):
        self._animations: dict[str, Animation] = {}
        self._current: Optional[Animation] = None
        self._frame_index: int = 0
        self._timer: float = 0.0
        self._finished: bool = False
    
    def add(self, animation: Animation):
        self._animations[animation.name] = animation
    
    def play(self, name: str):
        """播放指定动画。如果已经在播放同名动画则不中断。"""
        if self._current and self._current.name == name:
            return
        
        if name not in self._animations:
            return
        
        self._current = self._animations[name]
        self._frame_index = 0
        self._timer = 0.0
        self._finished = False
    
    def update(self, dt: float):
        if not self._current or self._finished:
            return
        
        self._timer += dt
        if self._timer >= self._current.frame_duration:
            self._timer = 0.0
            self._frame_index += 1
            
            if self._frame_index >= len(self._current.frames):
                if self._current.loop:
                    self._frame_index = 0
                else:
                    self._frame_index = len(self._current.frames) - 1
                    self._finished = True
                    if self._current.on_complete:
                        self._current.on_complete()
    
    @property
    def current_frame(self) -> Optional[pygame.Surface]:
        if self._current and self._current.frames:
            return self._current.frames[self._frame_index]
        return None
    
    @property
    def is_finished(self) -> bool:
        return self._finished
    
    def reset(self):
        self._current = None
        self._finished = True
```

**Step 2: 提交**

```bash
git add -A && git commit -m "feat: add animator with frame sequences and callbacks"
```

---

### Task 13: 实体工厂

**Objective:** 从 JSON 数据实例化实体，实现数据驱动。

**Files:**
- Create: `xianxia-rpg/entities/factory.py`
- Create: `xianxia-rpg/data/entities.json` (示例)

**Step 1: 写入实体数据示例**

```json
// data/entities.json
{
  "player": {
    "name": "主角",
    "size": [32, 32],
    "max_hp": 100,
    "base_speed": 120,
    "sprite_sheet": "sprites/player.png",
    "animations": {
      "idle": {"frames": [[0,0]], "duration": 0.5},
      "walk": {"frames": [[0,0],[1,0],[2,0],[3,0]], "duration": 0.15},
      "attack": {"frames": [[0,1],[1,1],[2,1]], "duration": 0.1, "loop": false}
    }
  },
  "slime": {
    "name": "史莱姆",
    "size": [32, 32],
    "max_hp": 30,
    "base_speed": 40,
    "sprite_sheet": "sprites/enemy_slime.png",
    "animations": {
      "idle": {"frames": [[0,0]], "duration": 0.5},
      "walk": {"frames": [[0,0],[1,0]], "duration": 0.2}
    }
  }
}
```

**Step 2: 写入工厂实现**

```python
# entities/factory.py
"""实体工厂：从 JSON 数据实例化实体。"""
import json
from pathlib import Path
from typing import Optional
from .entity import Entity
from .animator import Animator, Animation
from core.vector import Vector2
from core.resource_manager import ResourceManager
from core.logger import GameLogger

logger = GameLogger.get("factory")

class EntityFactory:
    def __init__(self, resource_mgr: ResourceManager, data_path: str = "data"):
        self._resources = resource_mgr
        self._data_path = Path(data_path)
        self._entity_defs: dict = {}
        self._load_definitions()
    
    def _load_definitions(self):
        entities_file = self._data_path / "entities.json"
        if entities_file.exists():
            with open(entities_file, "r", encoding="utf-8") as f:
                self._entity_defs = json.load(f)
            logger.info(f"Loaded {len(self._entity_defs)} entity definitions")
    
    def create(self, entity_type: str, pos: Vector2) -> Optional[Entity]:
        """根据类型创建实体。"""
        if entity_type not in self._entity_defs:
            logger.warning(f"Unknown entity type: {entity_type}")
            return None
        
        def_data = self._entity_defs[entity_type]
        size = Vector2(*def_data.get("size", [32, 32]))
        
        entity = Entity(
            entity_id=f"{entity_type}_{id(pos)}",
            pos=pos,
            size=size,
            max_hp=def_data.get("max_hp", 100),
            current_hp=def_data.get("max_hp", 100),
            base_speed=def_data.get("base_speed", 100),
        )
        
        # 加载精灵表和动画
        sheet_path = def_data.get("sprite_sheet")
        if sheet_path:
            try:
                frames = self._resources.load_spritesheet(sheet_path, size.x, size.y)
                entity.animation_frames = frames
                entity.sprite = frames[0] if frames else None
            except FileNotFoundError:
                logger.warning(f"Sprite not found: {sheet_path}")
        
        # 加载动画定义
        anim_defs = def_data.get("animations", {})
        animator = Animator()
        for anim_name, anim_data in anim_defs.items():
            frame_coords = anim_data.get("frames", [[0, 0]])
            anim_frames = []
            sheet_path = def_data.get("sprite_sheet")
            if sheet_path:
                try:
                    sheet = self._resources.load(sheet_path)
                    tile_w, tile_h = size.x, size.y
                    for col, row in frame_coords:
                        rect = pygame.Rect(col*tile_w, row*tile_h, tile_w, tile_h)
                        anim_frames.append(sheet.subsurface(rect))
                except:
                    anim_frames = entity.animation_frames
            
            if anim_frames:
                animator.add(Animation(
                    name=anim_name,
                    frames=anim_frames,
                    frame_duration=anim_data.get("duration", 0.15),
                    loop=anim_data.get("loop", True),
                ))
        
        return entity
```

**Step 3: 提交**

```bash
git add -A && git commit -m "feat: add entity factory for JSON-driven entity creation"
```

---

### Task 14: Tilemap 渲染系统

**Objective:** 实现 Tile 地图加载与渲染，支持从 JSON 加载地图数据。

**Files:**
- Create: `xianxia-rpg/world/tilemap.py`

**Step 1: 写入实现**

```python
# world/tilemap.py
"""Tilemap 渲染：从 JSON 加载地图，按 Tile 渲染。"""
import pygame
from pathlib import Path
from core.vector import Vector2
from core.resource_manager import ResourceManager
from core.camera import Camera

class Tilemap:
    def __init__(self, resource_mgr: ResourceManager):
        self._resources = resource_mgr
        self.tiles: list[list[int]] = []       # 2D 网格，0 = 空，>0 = tile 索引
        self.tile_size = 32
        self.tileset: pygame.Surface = None
        self.width = 0
        self.height = 0
        self.terrain_rects: list[pygame.Rect] = []  # 碰撞区域
    
    def load_from_json(self, map_path: str, tileset_path: str, tile_size: int = 32):
        """从 JSON 加载地图。"""
        import json
        
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.tile_size = tile_size
        self.tiles = data.get("tiles", [])
        self.width = len(self.tiles[0]) if self.tiles else 0
        self.height = len(self.tiles)
        
        self.tileset = self._resources.load(tileset_path)
        
        # 生成地形碰撞区域
        self.terrain_rects.clear()
        collision_tiles = data.get("collision_tiles", [])
        for tile_index in collision_tiles:
            for row in range(self.height):
                for col in range(self.width):
                    if self.tiles[row][col] == tile_index:
                        self.terrain_rects.append(pygame.Rect(
                            col * self.tile_size,
                            row * self.tile_size,
                            self.tile_size,
                            self.tile_size,
                        ))
    
    def render(self, screen: pygame.Surface, camera: Camera):
        """只渲染视口内的 Tile。"""
        if not self.tileset:
            return
        
        view_x, view_y, view_x2, view_y2 = camera.world_rect()
        
        start_col = max(0, view_x // self.tile_size - 1)
        start_row = max(0, view_y // self.tile_size - 1)
        end_col = min(self.width, view_x2 // self.tile_size + 2)
        end_row = min(self.height, view_y2 // self.tile_size + 2)
        
        tile_cols = self.tileset.get_width() // self.tile_size
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_index = self.tiles[row][col]
                if tile_index == 0:
                    continue
                
                screen_x, screen_y = camera.apply(Vector2(
                    col * self.tile_size,
                    row * self.tile_size,
                )).tuple()
                
                # 从 tileset 中取对应的 Tile
                src_col = (tile_index - 1) % tile_cols
                src_row = (tile_index - 1) // tile_cols
                src_rect = pygame.Rect(
                    src_col * self.tile_size,
                    src_row * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )
                
                screen.blit(self.tileset, (int(screen_x), int(screen_y)), src_rect)
    
    def get_terrain_rects(self) -> list[pygame.Rect]:
        return self.terrain_rects
```

**Step 2: 提交**

```bash
git add -A && git commit -m "feat: add tilemap system with viewport culling and terrain collision"
```

---

## Phase 3: 核心游戏系统（第15-22任务）

### Task 15: 玩家控制器

**Objective:** 实现玩家输入 → 移动 + 攻击的完整控制逻辑。

**Files:**
- Create: `xianxia-rpg/entities/player.py`
- Create: `xianxia-rpg/systems/combat.py`

**Step 1: 写入实现**

```python
# entities/player.py
"""玩家实体：处理输入、移动、攻击。"""
import pygame
from .entity import Entity
from .fsm import FSM, State
from core.vector import Vector2
from core.input_handler import InputHandler
from core.config import PhysicsConfig, CombatConfig

class Player(Entity):
    def __init__(self, entity_id: str = "player", pos: Vector2 = None):
        pos = pos or Vector2(0, 0)
        super().__init__(entity_id=entity_id, pos=pos, size=Vector2(32, 32))
        
        self.fsm = FSM()
        self._setup_states()
        
        # 战斗状态
        self.attack_timer: float = 0.0
        self.dodge_timer: float = 0.0
        self.dodge_cooldown: float = 0.0
        self.invincible: bool = False
        self.invincible_timer: float = 0.0
        
        # 配置
        self._physics = PhysicsConfig()
        self._combat = CombatConfig()
    
    def _setup_states(self):
        self.fsm.add_state(State("idle"))
        self.fsm.add_state(State("walk"))
        self.fsm.add_state(State("attack",
            on_update=self._attack_update,
        ))
        self.fsm.add_state(State("dodge",
            on_enter=self._dodge_enter,
            on_update=self._dodge_update,
        ))
    
    def handle_input(self, inp: InputHandler, dt: float):
        """处理玩家输入。"""
        if not self.is_alive:
            return
        
        # 更新计时器
        self.attack_timer = max(0, self.attack_timer - dt)
        self.dodge_cooldown = max(0, self.dodge_cooldown - dt)
        
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # 闪避（优先级最高）
        if inp.consume_action("dodge") and self.dodge_cooldown <= 0:
            if inp.is_direction_held():
                direction = inp.direction.normalized()
            else:
                direction = self._get_facing_direction()
            self.dodge(direction)
            return
        
        # 攻击
        if inp.consume_action("attack") and self.attack_timer <= 0:
            self.start_attack()
            return
        
        # 移动
        if inp.is_direction_held():
            move_dir = inp.direction.normalized()
            self.vel = move_dir * self.base_speed
            self.facing = self._direction_to_facing(move_dir)
            self.fsm.set_state("walk")
        else:
            self.vel = Vector2(0, 0)
            self.fsm.set_state("idle")
    
    def start_attack(self):
        self.attack_timer = self._combat.default_attack_cooldown
        self.fsm.set_state("attack", {"hit_done": False})
    
    def _attack_update(self, dt, params):
        # 攻击持续时间后回到 idle
        params["time"] = params.get("time", 0) + dt
        if params["time"] >= self._combat.default_attack_cooldown:
            self.fsm.set_state("idle")
    
    def dodge(self, direction: Vector2):
        self.dodge_cooldown = self._physics.dodge_cooldown
        self.invincible = True
        self.invincible_timer = self._physics.dodge_duration
        self.vel = direction * self._physics.dodge_distance / self._physics.dodge_duration
        self.fsm.set_state("dodge", {"elapsed": 0})
    
    def _dodge_enter(self, params):
        params["elapsed"] = 0
    
    def _dodge_update(self, dt, params):
        params["elapsed"] += dt
        if params["elapsed"] >= self._physics.dodge_duration:
            self.fsm.set_state("idle")
    
    def _get_facing_direction(self) -> Vector2:
        mapping = {
            "up": Vector2(0, -1), "down": Vector2(0, 1),
            "left": Vector2(-1, 0), "right": Vector2(1, 0),
        }
        return mapping.get(self.facing, Vector2(0, 1))
    
    def _direction_to_facing(self, direction: Vector2) -> str:
        if abs(direction.x) > abs(direction.y):
            return "right" if direction.x > 0 else "left"
        return "down" if direction.y > 0 else "up"
    
    def get_attack_rect(self) -> pygame.Rect:
        """获取攻击判定框。"""
        facing_rects = {
            "up": (-8, -40, 48, 40),
            "down": (-8, 32, 48, 40),
            "left": (-40, -8, 40, 48),
            "right": (32, -8, 40, 48),
        }
        rx, ry, rw, rh = facing_rects.get(self.facing, (-8, 32, 48, 40))
        return pygame.Rect(
            int(self.pos.x + rx),
            int(self.pos.y + ry),
            rw, rh,
        )
    
    def update(self, dt: float):
        super().update(dt)
        self.fsm.update(dt)
    
    def render(self, screen: pygame.Surface, camera):
        if self.invincible:
            # 闪烁效果
            import time
            if int(time.time() * 10) % 2 == 0:
                return
        super().render(screen, camera)
```

```python
# systems/combat.py
"""战斗系统：处理攻击判定、伤害计算、投射物。"""
import pygame
from typing import Optional
from core.vector import Vector2
from core.event_bus import EventBus
from core.config import CombatConfig
from entities.entity import Entity
from core.collision import CollisionSystem

class Projectile(Entity):
    """投射物实体。"""
    def __init__(self, pos: Vector2, direction: Vector2, damage: float, speed: float = 300):
        super().__init__(
            entity_id=f"projectile_{id(pos)}",
            pos=pos,
            size=Vector2(16, 16),
            max_hp=1,
            current_hp=1,
        )
        self.vel = direction.normalized() * speed
        self.damage = damage
        self.lifetime = 2.0  # 2秒后消失
        self.owner_id: str = ""  # 发射者ID
    
    def update(self, dt: float):
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_alive = False

class CombatSystem:
    def __init__(self, collision: CollisionSystem):
        self._collision = collision
        self._projectiles: list[Projectile] = []
        self._config = CombatConfig()
    
    def spawn_projectile(self, pos: Vector2, direction: Vector2, damage: float, owner_id: str):
        proj = Projectile(pos, direction, damage)
        proj.owner_id = owner_id
        self._projectiles.append(proj)
    
    def update_projectiles(self, dt: float, enemies: list[Entity]):
        for proj in self._projectiles:
            if not proj.is_alive:
                continue
            proj.update(dt)
            
            # 检测投射物与敌人的碰撞
            for enemy in enemies:
                if not enemy.is_alive:
                    continue
                if proj.get_collision_rect().colliderect(enemy.get_collision_rect()):
                    enemy.take_damage(proj.damage, proj.pos)
                    proj.is_alive = False
                    break
        
        # 清理死亡投射物
        self._projectiles = [p for p in self._projectiles if p.is_alive]
    
    def get_attack_hitbox(self, player) -> pygame.Rect:
        return player.get_attack_rect()
```

**Step 2: 提交**

```bash
git add -A && git commit -m "feat: add player controller with input, movement, attack, dodge"
```

---

### Task 16: 敌人 AI 系统

**Objective:** 实现敌人巡逻/追击/攻击 AI，使用 BFS 路径规划。

**Files:**
- Create: `xianxia-rpg/entities/enemy.py`
- Create: `xianxia-rpg/systems/pathfinding.py`

（内容类似，因篇幅限制，列出关键结构）

---

### Task 17: 修炼系统（核心差异化）

**Objective:** 实现修炼、突破、天劫系统，从 JSON 读取境界数据。

**Files:**
- Create: `xianxia-rpg/systems/cultivation.py`
- Create: `xianxia-rpg/data/realms.json`

---

### Task 18: 背包与装备系统

**Objective:** 实现背包管理、装备穿戴、属性加成计算。

**Files:**
- Create: `xianxia-rpg/systems/inventory.py`
- Create: `xianxia-rpg/data/items.json`
- Create: `xianxia-rpg/data/equipment.json`

---

### Task 19: 对话与任务系统

**Objective:** 实现对话树解析、分支选择、任务目标追踪。

**Files:**
- Create: `xianxia-rpg/systems/dialogue.py`
- Create: `xianxia-rpg/systems/quest.py`
- Create: `xianxia-rpg/data/dialogues.json`
- Create: `xianxia-rpg/data/quests.json`

---

### Task 20: 场景/房间系统

**Objective:** 实现多房间管理、传送门、实体初始化。

**Files:**
- Create: `xianxia-rpg/world/room.py`
- Create: `xianxia-rpg/world/map_loader.py`
- Create: `xianxia-rpg/maps/room_start.json`

---

### Task 21: 存档系统

**Objective:** 实现 JSON 存档、版本校验、多存档位。

**Files:**
- Create: `xianxia-rpg/systems/save_load.py`

---

### Task 22: UI 框架与 HUD

**Objective:** 实现通用 UI 组件、游戏内 HUD。

**Files:**
- Create: `xianxia-rpg/ui/hud.py`
- Create: `xianxia-rpg/ui/dialogue_ui.py`
- Create: `xianxia-rpg/ui/menu.py`

---

## Phase 4: 集成与打磨（第23-26任务）

### Task 23: 游戏主循环集成

**Objective:** 将所有系统集成到主循环，实现可玩的游戏。

### Task 24: 音效系统

**Objective:** 实现 BGM 和 SFX 管理。

### Task 25: 粒子特效

**Objective:** 实现粒子系统（受击、升级、突破特效）。

### Task 26: 数据填充与测试

**Objective:** 填入完整游戏数据（剧本对话、地图、敌人），进行端到端测试。

---

## 开发里程碑

| 阶段 | 任务 | 预计时间 | 可验证里程碑 |
|------|------|---------|-------------|
| **Phase 1** | Task 1-8 | 1-2周 | 空窗口+配置+输入+摄像机+资源管理 |
| **Phase 2** | Task 9-14 | 1-2周 | 玩家实体可移动、碰撞、动画播放 |
| **Phase 3** | Task 15-22 | 3-4周 | 完整游戏循环：移动→战斗→修炼→背包→对话→存档 |
| **Phase 4** | Task 23-26 | 2-3周 | 可发布版本，含完整数据和音效 |

---

## 外部结构验证清单

每个 Task 完成后需验证：
- [ ] 代码中无硬编码游戏内容（如"炼气期"、"青云宗"）
- [ ] 所有游戏特定数据来自 JSON 配置文件
- [ ] 更换 JSON 数据后引擎仍能正常运行
- [ ] 新增内容只需添加 JSON 和资产，无需修改引擎代码

---

## 执行方式

后续开发将按以下流程进行：
1. 每个 Task 由独立子代理实现
2. 两轮审查：规范符合性 → 代码质量
3. 通过后标记完成，进入下一 Task
4. 每个 Phase 完成后进行集成测试

**计划文档路径**: `xianxia-rpg/docs/development_plan.md`

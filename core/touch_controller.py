"""触屏控制器：虚拟摇杆 + 动作按钮。"""
import pygame
from dataclasses import dataclass, field
from typing import Optional
from core.vector import Vector2


@dataclass
class TouchZone:
    """触摸区域定义。"""
    name: str
    rect: pygame.Rect
    action: str  # 对应的动作名称


class TouchController:
    """Android 触屏输入控制器。
    
    布局：
    - 左下 1/3 屏幕: 虚拟摇杆 (移动)
    - 右下区域: 4 个动作按钮 (攻击/技能/闪避/互动)
    - 顶部 HUD 区域: 屏蔽触摸防误触
    """
    
    # 防误触区域（顶部 HUD 高度比例）
    HUD_TOP_RATIO = 0.08
    # 底部技能栏高度比例
    BOTTOM_BAR_RATIO = 0.15
    # 摇杆区域比例
    JOYSTICK_X_RATIO = 0.30
    JOYSTICK_Y_RATIO = 0.35
    # 按钮区域比例
    BUTTON_X_RATIO = 0.22
    BUTTON_Y_RATIO = 0.22
    BUTTON_SPACING = 15
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 方向输出（-1.0 ~ 1.0）
        self.direction = Vector2(0, 0)
        
        # 动作按钮状态
        self.action_pressed: dict[str, bool] = {
            "attack": False,
            "skill": False,
            "dodge": False,
            "interact": False,
        }
        
        # 动作刚按下（用于 just-pressed 检测）
        self.action_just_pressed: dict[str, bool] = {
            "attack": False,
            "skill": False,
            "dodge": False,
            "interact": False,
        }
        
        # 摇杆状态
        self._joystick_center: Vector2 = Vector2(0, 0)
        self._joystick_radius: float = 40.0
        self._joystick_touch_id: Optional[int] = None
        self._joystick_active = False
        
        # 按钮状态
        self._button_touches: dict[int, str] = {}  # finger_id -> button_name
        self._prev_button_state: dict[str, bool] = {}
        
        # 触摸追踪（所有活动触摸点）
        self._touches: dict[int, Vector2] = {}
        
        # 计算布局
        self._calculate_layout()
    
    def _calculate_layout(self):
        """根据屏幕尺寸计算触摸区域。"""
        sw, sh = self.screen_width, self.screen_height
        
        # 摇杆中心：左下角区域
        self._joystick_center = Vector2(
            sw * self.JOYSTICK_X_RATIO * 0.5,
            sh * (1.0 - self.JOYSTICK_Y_RATIO * 0.5)
        )
        self._joystick_radius = min(sw, sh) * 0.08
        
        # 4 个动作按钮（菱形排列）
        btn_size = min(sw * self.BUTTON_X_RATIO, sh * self.BUTTON_Y_RATIO)
        spacing = self.BUTTON_SPACING
        base_x = sw - btn_size * 1.5 - spacing
        base_y = sh - btn_size * 2.5 - spacing
        
        self._buttons: list[TouchZone] = [
            TouchZone("attack", pygame.Rect(
                int(base_x + btn_size + spacing), int(base_y),
                int(btn_size), int(btn_size)
            ), "attack"),
            TouchZone("skill", pygame.Rect(
                int(base_x), int(base_y + btn_size + spacing),
                int(btn_size), int(btn_size)
            ), "skill"),
            TouchZone("dodge", pygame.Rect(
                int(base_x + btn_size + spacing), int(base_y + btn_size + spacing),
                int(btn_size), int(btn_size)
            ), "dodge"),
            TouchZone("interact", pygame.Rect(
                int(base_x), int(base_y),
                int(btn_size), int(btn_size)
            ), "interact"),
        ]
        
        # HUD 防误触区域
        self._hud_rect = pygame.Rect(0, 0, sw, int(sh * self.HUD_TOP_RATIO))
    
    def handle_event(self, event) -> None:
        """处理 pygame 触屏事件。"""
        if event.type == pygame.FINGERDOWN:
            self._on_finger_down(event)
        elif event.type == pygame.FINGERMOTION:
            self._on_finger_motion(event)
        elif event.type == pygame.FINGERUP:
            self._on_finger_up(event)
    
    def _get_screen_pos(self, event) -> Vector2:
        """将触屏事件坐标转换为屏幕像素坐标。"""
        return Vector2(
            event.dict['x'] * self.screen_width,
            event.dict['y'] * self.screen_height
        )
    
    def _on_finger_down(self, event) -> None:
        finger_id = event.dict['finger_id']
        pos = self._get_screen_pos(event)
        
        # 顶部 HUD 区域屏蔽触摸
        if self._hud_rect.collidepoint(pos.x, pos.y):
            return
        
        self._touches[finger_id] = pos
        
        # 检查是否按下按钮
        for btn in self._buttons:
            if btn.rect.collidepoint(pos.x, pos.y):
                self._button_touches[finger_id] = btn.action
                self._prev_button_state[btn.action] = self.action_pressed.get(btn.action, False)
                self.action_pressed[btn.action] = True
                return
        
        # 否则视为摇杆触摸（如果触摸在左半屏）
        if pos.x < self.screen_width * 0.5:
            self._joystick_touch_id = finger_id
            self._joystick_active = True
            self._update_joystick(pos)
    
    def _on_finger_motion(self, event) -> None:
        finger_id = event.dict['finger_id']
        pos = self._get_screen_pos(event)
        self._touches[finger_id] = pos
        
        # 更新摇杆
        if finger_id == self._joystick_touch_id and self._joystick_active:
            self._update_joystick(pos)
    
    def _on_finger_up(self, event) -> None:
        finger_id = event.dict['finger_id']
        
        if finger_id in self._touches:
            del self._touches[finger_id]
        
        # 松开按钮
        if finger_id in self._button_touches:
            btn_name = self._button_touches[finger_id]
            self.action_pressed[btn_name] = False
            del self._button_touches[finger_id]
        
        # 松开摇杆
        if finger_id == self._joystick_touch_id:
            self._joystick_active = False
            self._joystick_touch_id = None
            self.direction = Vector2(0, 0)
    
    def _update_joystick(self, pos: Vector2) -> None:
        """更新虚拟摇杆方向。"""
        delta = pos - self._joystick_center
        dist = delta.length()
        
        if dist < self._joystick_radius * 0.3:
            # 死区
            self.direction = Vector2(0, 0)
        else:
            # 归一化
            if dist > self._joystick_radius:
                delta = delta.normalized() * self._joystick_radius
            self.direction = delta.normalized()
    
    def update(self, dt: float) -> None:
        """每帧调用，更新 just-pressed 状态。"""
        for action in self.action_pressed:
            prev = self._prev_button_state.get(action, False)
            curr = self.action_pressed.get(action, False)
            self.action_just_pressed[action] = curr and not prev
            self._prev_button_state[action] = curr
    
    def reset_just_pressed(self) -> None:
        """清除 just-pressed 状态（每帧末调用）。"""
        for action in self.action_just_pressed:
            self.action_just_pressed[action] = False
    
    def consume_action(self, action_name: str) -> bool:
        """消耗动作（类似 InputHandler.consume_action）。"""
        if self.action_just_pressed.get(action_name, False):
            self.action_just_pressed[action_name] = False
            return True
        return False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染虚拟摇杆和按钮。"""
        alpha = 80
        color = (200, 200, 200)
        active_color = (255, 220, 100)
        
        # 摇杆底座
        joy_surf = pygame.Surface(
            (int(self._joystick_radius * 2.5), int(self._joystick_radius * 2.5)),
            pygame.SRCALPHA
        )
        joy_surf.fill((0, 0, 0, 40))
        pygame.draw.circle(joy_surf, (*color, alpha),
                         (int(self._joystick_radius * 1.25), int(self._joystick_radius * 1.25)),
                         int(self._joystick_radius * 1.25), 2)
        screen.blit(joy_surf, (
            int(self._joystick_center.x - self._joystick_radius * 1.25),
            int(self._joystick_center.y - self._joystick_radius * 1.25)
        ))
        
        # 摇杆头
        if self._joystick_active:
            head_offset = self.direction * self._joystick_radius
            head_pos = self._joystick_center + head_offset
        else:
            head_pos = self._joystick_center
        
        pygame.draw.circle(screen, (*active_color, 120),
                         (int(head_pos.x), int(head_pos.y)),
                         int(self._joystick_radius * 0.45))
        
        # 动作按钮
        for btn in self._buttons:
            color = active_color if self.action_pressed.get(btn.action, False) else color
            surf = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
            surf.fill((30, 30, 50, 100))
            pygame.draw.rect(surf, (*color, alpha), surf.get_rect(), 2)
            
            # 按钮文字
            labels = {"attack": "攻", "skill": "技", "dodge": "闪", "interact": "交"}
            font = pygame.font.SysFont("sans-serif", max(14, int(btn.rect.width * 0.3)))
            txt = font.render(labels.get(btn.action, btn.action[:1]), True, color)
            surf.blit(txt, (
                (btn.rect.width - txt.get_width()) // 2,
                (btn.rect.height - txt.get_height()) // 2
            ))
            
            screen.blit(surf, btn.rect.topleft)

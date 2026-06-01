#!/usr/bin/env python3
"""
Desktop Pet for Mac — PyObjC 버전
frame1.png, frame2.png 를 같은 폴더에 두고 실행하세요
종료: 메뉴바 🐹 → 종료
"""

import random
import sys
import os
import time
import io
from PIL import Image
from AppKit import (
    NSApplication,
    NSWindow,
    NSWindowStyleMaskBorderless,
    NSBackingStoreBuffered,
    NSScreen,
    NSColor,
    NSImageView,
    NSImage,
    NSData,
    NSEvent,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSFloatingWindowLevel,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
)
from Foundation import NSObject, NSTimer

# ── 전역 설정 (run_pet()에서 덮어씀) ─────────────────────────
FRAMES = []
FOLLOW_MOUSE = True
PET_SCALE = 0.08
MOVE_SPEED = 4
FOLLOW_SPEED = 3
ANIM_INTERVAL = 0.3

# ── 고정 상수 ─────────────────────────────────────────────────
MOVE_INTERVAL = 0.05
IDLE_CHANCE = 0.003
IDLE_DURATION = 2.0
FOLLOW_THRESHOLD = 30
# ─────────────────────────────────────────────────────────────


class TickDelegate(NSObject):
    def initWithPet_(self, pet):
        self = super().init()
        if self:
            self.pet = pet
            self.last = time.time()
        return self

    def tick_(self, timer):
        now = time.time()
        dt = now - self.last
        self.last = now
        self.pet.tick(dt)


def pil_to_nsimage(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    data = NSData.dataWithBytes_length_(buf.getvalue(), len(buf.getvalue()))
    return NSImage.alloc().initWithData_(data)


def load_frames():
    frames, frames_flipped = [], []
    w = h = 0
    for path in FRAMES:
        if not os.path.exists(path):
            print(f"[오류] '{path}' 파일이 없어요.")
            sys.exit(1)
        img = Image.open(path).convert("RGBA")
        w = int(img.width * PET_SCALE)
        h = int(img.height * PET_SCALE)
        img = img.resize((w, h), Image.LANCZOS)
        frames.append(pil_to_nsimage(img))
        frames_flipped.append(pil_to_nsimage(img.transpose(Image.FLIP_LEFT_RIGHT)))
    print(f"[로드 완료] 프레임: {len(frames)}, 크기: {w}x{h}")
    return frames, frames_flipped, w, h


class QuitHandler(NSObject):
    def quit_(self, sender):
        global APP_TIMER
        print("[종료]")
        if APP_TIMER:
            APP_TIMER.invalidate()
        from AppKit import NSApp

        NSApp.terminate_(None)
        os._exit(0)


class DesktopPet:
    def __init__(self):
        self.frames, self.frames_flipped, self.pw, self.ph = load_frames()
        self.frame_count = len(self.frames)
        self.current_frame = 0
        self.facing_right = True
        self.idle = False
        self.idle_timer = 0.0
        self.anim_accum = 0.0
        self.move_accum = 0.0

        screen = NSScreen.mainScreen().frame()
        self.sw = int(screen.size.width)
        self.sh = int(screen.size.height)

        self.x = random.randint(0, self.sw - self.pw)
        self.y = random.randint(self.sh // 4, self.sh // 2)
        self.dx = MOVE_SPEED * random.choice([-1, 1])
        self.dy = 0
        self.facing_right = self.dx > 0

        self._create_window()

    def _create_window(self):
        rect = ((self.x, self.y), (self.pw, self.ph))
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
        )
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setOpaque_(False)
        self.window.setHasShadow_(False)
        self.window.setLevel_(NSFloatingWindowLevel + 1)
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
        )
        self.window.setIgnoresMouseEvents_(True)

        self.image_view = NSImageView.alloc().initWithFrame_(
            ((0, 0), (self.pw, self.ph))
        )
        self.image_view.setImageScaling_(2)
        self.window.contentView().addSubview_(self.image_view)
        self.window.makeKeyAndOrderFront_(None)
        self._update_frame()
        self._create_menu_bar()
        print("[창] 생성 완료 — 펫 등장!")

    def _create_menu_bar(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)
        self.status_item.button().setTitle_("🐹")

        menu = NSMenu.alloc().init()
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "종료", "quit:", ""
        )
        self.quit_handler = QuitHandler.alloc().init()
        quit_item.setTarget_(self.quit_handler)
        menu.addItem_(quit_item)
        self.status_item.setMenu_(menu)

    def _update_frame(self):
        frames = self.frames if self.facing_right else self.frames_flipped
        self.image_view.setImage_(frames[self.current_frame])

    def _get_mouse_pos(self):
        p = NSEvent.mouseLocation()
        return int(p.x), int(p.y)

    def tick(self, dt):
        # 애니메이션
        self.anim_accum += dt
        if self.anim_accum >= ANIM_INTERVAL:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self._update_frame()
            self.anim_accum = 0.0

        # 이동
        self.move_accum += dt
        if self.move_accum < MOVE_INTERVAL:
            return
        self.move_accum = 0.0

        # ← bool 비교로 분기
        if FOLLOW_MOUSE:
            self._tick_follow()
        else:
            self._tick_wander()

        self.window.setFrameOrigin_((self.x, self.y))

    def _tick_follow(self):
        mx, my = self._get_mouse_pos()
        cx = self.x + self.pw // 2
        cy = self.y + self.ph // 2
        dist_x = mx - cx
        dist_y = my - cy
        dist = (dist_x**2 + dist_y**2) ** 0.5

        if dist < FOLLOW_THRESHOLD:
            return

        self.facing_right = dist_x > 0
        step = min(FOLLOW_SPEED, dist)
        self.x += int(dist_x / dist * step)
        self.y += int(dist_y / dist * step)

    def _tick_wander(self):
        if self.idle:
            self.idle_timer -= MOVE_INTERVAL
            if self.idle_timer <= 0:
                self.idle = False
                self.dx = MOVE_SPEED * random.choice([-1, 1])
                self.dy = 0
                self.facing_right = self.dx > 0
            return

        if random.random() < IDLE_CHANCE:
            self.idle = True
            self.idle_timer = IDLE_DURATION
            return

        if random.random() < 0.02:
            self.dy = random.choice([-1, 0, 0, 1]) * MOVE_SPEED // 2

        self.x += self.dx
        self.y += self.dy

        if self.x <= 0:
            self.x = 0
            self.dx = abs(self.dx)
            self.facing_right = True
        elif self.x >= self.sw - self.pw:
            self.x = self.sw - self.pw
            self.dx = -abs(self.dx)
            self.facing_right = False

        floor, ceiling = self.sh - self.ph - 80, self.sh // 4
        if self.y < ceiling:
            self.y = ceiling
            self.dy = abs(self.dy)
        elif self.y > floor:
            self.y = floor
            self.dy = -abs(self.dy)


def run_pet(frame1, frame2, config: dict):
    """
    config 키:
        follow_mouse  : bool
        pet_scale     : float  (예: 0.08)
        move_speed    : int    (예: 4)
        follow_speed  : int    (예: 3)
        anim_interval : float  (예: 0.3)
    """
    global FRAMES, FOLLOW_MOUSE, PET_SCALE, MOVE_SPEED, FOLLOW_SPEED, ANIM_INTERVAL

    FRAMES = [frame1, frame2]
    FOLLOW_MOUSE = bool(config.get("follow_mouse", True))  # ← 반드시 bool
    PET_SCALE = float(config.get("pet_scale", 0.08))
    MOVE_SPEED = int(config.get("move_speed", 4))
    FOLLOW_SPEED = int(config.get("follow_speed", 3))
    ANIM_INTERVAL = float(config.get("anim_interval", 0.3))

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(0)

    pet = DesktopPet()
    delegate = TickDelegate.alloc().initWithPet_(pet)

    global APP_TIMER
    APP_TIMER = (
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.016,
            delegate,
            "tick:",
            None,
            True,
        )
    )

    app.run()

#!/usr/bin/env python3
"""
Desktop Pet Launcher
- GUI로 설정 입력 후 데스크탑 펫 실행
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from desktop_pet import run_pet


class Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("🐹 Desktop Pet Launcher")
        self.root.resizable(False, False)

        self.frame1_path = tk.StringVar()
        self.frame2_path = tk.StringVar()
        self.follow_mouse = tk.BooleanVar(value=True)

        # 슬라이더 변수
        self.pet_scale = tk.DoubleVar(value=0.08)
        self.move_speed = tk.IntVar(value=4)
        self.follow_speed = tk.IntVar(value=3)
        self.anim_interval = tk.DoubleVar(value=0.3)

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_ui(self):
        pad = dict(padx=16, pady=6)

        # ── 타이틀 ──────────────────────────────────
        tk.Label(self.root, text="🐹 Desktop Pet", font=("Helvetica", 20, "bold")).pack(
            pady=(24, 4)
        )
        tk.Label(
            self.root,
            text="PNG 파일 두 장을 선택하고 펫을 실행하세요",
            font=("Helvetica", 11),
            fg="#666",
        ).pack(pady=(0, 12))

        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16)

        # ── 이미지 파일 선택 ────────────────────────
        self._file_row("프레임 1 (PNG)", self.frame1_path)
        self._file_row("프레임 2 (PNG)", self.frame2_path)

        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16, pady=4)

        # ── 옵션: 마우스 따라다니기 ─────────────────
        opt_frame = tk.Frame(self.root)
        opt_frame.pack(fill="x", **pad)
        tk.Label(opt_frame, text="마우스 따라다니기", font=("Helvetica", 12)).pack(
            side="left"
        )
        tk.Checkbutton(
            opt_frame, variable=self.follow_mouse, font=("Helvetica", 12)
        ).pack(side="right")

        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16, pady=4)

        # ── 슬라이더 섹션 ────────────────────────────
        tk.Label(self.root, text="⚙️  상세 설정", font=("Helvetica", 13, "bold")).pack(
            anchor="w", padx=16, pady=(6, 2)
        )

        self._slider_row(
            "캐릭터 크기", self.pet_scale, 0.03, 0.30, 0.01, fmt=lambda v: f"{v:.2f}"
        )
        self._slider_row("배회 속도", self.move_speed, 1, 12, 1)
        self._slider_row("마우스 추적 속도", self.follow_speed, 1, 10, 1)
        self._slider_row(
            "애니메이션 속도",
            self.anim_interval,
            0.05,
            1.0,
            0.05,
            fmt=lambda v: f"{v:.2f}s",
        )

        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16, pady=8)

        # ── 실행 버튼 ────────────────────────────────
        tk.Button(
            self.root,
            text="  펫 실행하기  ",
            font=("Helvetica", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            relief="flat",
            cursor="hand2",
            command=self._launch,
            padx=12,
            pady=8,
        ).pack(pady=20)

    # ── 파일 선택 행 ─────────────────────────────────
    def _file_row(self, label, var):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=16, pady=6)
        tk.Label(frame, text=label, font=("Helvetica", 12), width=16, anchor="w").pack(
            side="left"
        )
        tk.Entry(
            frame, textvariable=var, font=("Helvetica", 11), width=28, fg="#333"
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            frame,
            text="찾기",
            font=("Helvetica", 11),
            relief="flat",
            bg="#eee",
            cursor="hand2",
            command=lambda v=var: self._browse(v),
        ).pack(side="left")

    # ── 슬라이더 행 ──────────────────────────────────
    def _slider_row(self, label, var, from_, to, resolution, fmt=None):
        if fmt is None:
            fmt = lambda v: str(int(v))

        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=16, pady=4)

        tk.Label(frame, text=label, font=("Helvetica", 11), width=18, anchor="w").pack(
            side="left"
        )

        val_lbl = tk.Label(
            frame,
            text=fmt(var.get()),
            font=("Helvetica", 11),
            width=6,
            anchor="e",
            fg="#333",
        )
        val_lbl.pack(side="right")

        def on_change(v, lbl=val_lbl, f=fmt):
            lbl.config(text=f(float(v)))

        tk.Scale(
            frame,
            variable=var,
            from_=from_,
            to=to,
            resolution=resolution,
            orient="horizontal",
            length=220,
            showvalue=False,
            command=on_change,
            troughcolor="#ddd",
            bg=self.root.cget("bg"),
            highlightthickness=0,
        ).pack(side="left", padx=(0, 4))

    def _browse(self, var):
        path = filedialog.askopenfilename(
            filetypes=[("PNG 파일", "*.png"), ("모든 파일", "*.*")]
        )
        if path:
            var.set(path)

    def _launch(self):
        f1 = self.frame1_path.get().strip()
        f2 = self.frame2_path.get().strip()

        if not f1 or not f2:
            messagebox.showwarning("입력 필요", "PNG 파일 두 장을 모두 선택해주세요!")
            return
        if not os.path.exists(f1):
            messagebox.showerror("파일 오류", f"파일을 찾을 수 없어요:\n{f1}")
            return
        if not os.path.exists(f2):
            messagebox.showerror("파일 오류", f"파일을 찾을 수 없어요:\n{f2}")
            return

        config = {
            "follow_mouse": bool(self.follow_mouse.get()),  # ← 반드시 bool로 전달
            "pet_scale": float(self.pet_scale.get()),
            "move_speed": int(self.move_speed.get()),
            "follow_speed": int(self.follow_speed.get()),
            "anim_interval": float(self.anim_interval.get()),
        }

        self.root.destroy()
        run_pet(f1, f2, config)


def main():
    root = tk.Tk()
    Launcher(root)
    root.mainloop()


if __name__ == "__main__":
    main()

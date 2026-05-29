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
        pad = dict(padx=16, pady=8)

        # 타이틀
        tk.Label(self.root, text="🐹 Desktop Pet", font=("Helvetica", 20, "bold")).pack(
            pady=(24, 4)
        )
        tk.Label(
            self.root,
            text="PNG 파일 두 장을 선택하고 펫을 실행하세요",
            font=("Helvetica", 11),
            fg="#666",
        ).pack(pady=(0, 16))

        # 구분선
        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16)

        # 프레임 1
        self._file_row("프레임 1 (PNG)", self.frame1_path)
        # 프레임 2
        self._file_row("프레임 2 (PNG)", self.frame2_path)

        # 구분선
        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16, pady=8)

        # 마우스 따라다니기 옵션
        opt_frame = tk.Frame(self.root)
        opt_frame.pack(fill="x", **pad)
        tk.Label(opt_frame, text="마우스 따라다니기", font=("Helvetica", 12)).pack(
            side="left"
        )
        tk.Checkbutton(
            opt_frame, variable=self.follow_mouse, font=("Helvetica", 12)
        ).pack(side="right")

        # 구분선
        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=16)

        # 실행 버튼
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
        ).pack(pady=24)

    def _file_row(self, label, var):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=16, pady=6)

        tk.Label(frame, text=label, font=("Helvetica", 12), width=16, anchor="w").pack(
            side="left"
        )

        entry = tk.Entry(
            frame, textvariable=var, font=("Helvetica", 11), width=30, fg="#333"
        )
        entry.pack(side="left", padx=(0, 8))

        tk.Button(
            frame,
            text="찾기",
            font=("Helvetica", 11),
            relief="flat",
            bg="#eee",
            cursor="hand2",
            command=lambda v=var: self._browse(v),
        ).pack(side="left")

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

        follow = "1" if self.follow_mouse.get() else "0"

        # 펫 실행 (별도 프로세스)
        self.root.destroy()
        run_pet(f1, f2, follow)


def main():
    root = tk.Tk()
    Launcher(root)
    root.mainloop()


if __name__ == "__main__":
    main()

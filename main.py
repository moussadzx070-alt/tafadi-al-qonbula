import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
import random
import copy

# --- الألوان (ثيم عصري للعبة) ---
BG_COLOR = "#1a1a2e"          # خلفية اللعبة
PANEL_COLOR = "#16213e"       # لون اللوحات
SLOT_COLOR = "#0f3460"        # لون الأماكن الثابتة
ACCENT_COLOR = "#e94560"      # لون التحديد (القنبلة، إلخ)
TEXT_COLOR = "#ffffff"        # لون النصوص
BTN_STAY = "#2ecc71"          # لون زر البقاء
BTN_HOME = "#f1c40f"          # لون زر العودة
# ------------------------------

class Player:
    def __init__(self, pid, name, image_path, original_slot):
        self.pid = pid
        self.name = name
        self.original_slot = original_slot
        self.current_slot = original_slot
        self.is_alive = True
        self.decision = None
        
        # حفظ الصورة الأصلية لاستخدامها في حالات مختلفة (حي، ميت، محدد)
        self.raw_image = self._load_and_crop(image_path)
        self.img_normal = self._create_avatar(self.raw_image, border_color="#ffffff")
        self.img_highlight = self._create_avatar(self.raw_image, border_color="#3498db", border_width=4)
        self.img_dead = self._create_dead_avatar(self.raw_image)

    def _load_and_crop(self, path):
        try:
            img = Image.open(path).convert("RGBA")
        except:
            img = Image.new("RGBA", (200, 200), (100, 100, 100, 255))
        # قص الصورة لتصبح مربعة أولاً
        min_side = min(img.size)
        left = (img.width - min_side)/2
        top = (img.height - min_side)/2
        img = img.crop((left, top, left+min_side, top+min_side))
        return img.resize((90, 90), Image.Resampling.LANCZOS)

    def _create_avatar(self, img, border_color, border_width=2):
        size = img.size
        # قناع دائري
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        output = img.copy()
        output.putalpha(mask)
        
        # إضافة حدود دائرية
        final = Image.new("RGBA", size, (0,0,0,0))
        final.paste(output, (0,0), output)
        draw_final = ImageDraw.Draw(final)
        draw_final.ellipse((0, 0, size[0]-1, size[1]-1), outline=border_color, width=border_width)
        
        return ImageTk.PhotoImage(final)

    def _create_dead_avatar(self, img):
        size = img.size
        # جعل الصورة أبيض وأسود وشفافة جزئياً
        gray = img.convert("L").convert("RGBA")
        
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=150) # شفافية 150
        
        gray.putalpha(mask)
        
        # رسم علامة X حمراء
        draw_x = ImageDraw.Draw(gray)
        draw_x.line((20, 20, size[0]-20, size[1]-20), fill="red", width=8)
        draw_x.line((size[0]-20, 20, 20, size[1]-20), fill="red", width=8)
        
        return ImageTk.PhotoImage(gray)


class BombDodgeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("تفادي القنبلة - Bomb Dodge")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        
        self.players = []
        self.slots = []
        self.bomb_slot = -1
        self.round = 1
        self.cycle = 1
        
        self.canvas = tk.Canvas(self, width=1200, height=800, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.show_setup_screen()

    def clear_canvas(self):
        self.canvas.delete("all")

    # --- دوال مساعدة للرسم على الشاشة ---
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
                  x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2,
                  x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius,
                  x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_button(self, x, y, width, height, text, color, tag):
        self.create_rounded_rect(x, y, x+width, y+height, radius=20, fill=color, outline="", tags=(tag, "btn"))
        self.canvas.create_text(x+width/2, y+height/2, text=text, fill=TEXT_COLOR, font=("Arial", 16, "bold"), tags=(tag, "btn"))
        # إضافة تأثير تفاعلي عند تمرير الماوس
        self.canvas.tag_bind(tag, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

    # ================= شاشة الإعداد =================
    def show_setup_screen(self):
        self.clear_canvas()
        self.canvas.create_text(600, 80, text="إعداد اللاعبين (2 إلى 24 لاعب)", fill=TEXT_COLOR, font=("Arial", 32, "bold"))
        
        # أزرار الإضافة والبدء
        self.draw_button(400, 680, 200, 50, "إضافة لاعب +", BTN_STAY, "add_btn")
        self.canvas.tag_bind("add_btn", "<Button-1>", lambda e: self.add_player())
        
        self.draw_button(620, 680, 200, 50, "بدء اللعبة ▶", ACCENT_COLOR, "start_btn")
        self.canvas.tag_bind("start_btn", "<Button-1>", lambda e: self.start_game())
        
        self.draw_setup_players()

    def draw_setup_players(self):
        self.canvas.delete("setup_player")
        x_start, y_start = 100, 180
        for i, p in enumerate(self.players):
            row = i // 8
            col = i % 8
            x = x_start + (col * 130)
            y = y_start + (row * 150)
            
            self.canvas.create_image(x, y, anchor="nw", image=p.img_normal, tags="setup_player")
            self.canvas.create_text(x+45, y+110, text=p.name, fill=TEXT_COLOR, font=("Arial", 12, "bold"), tags="setup_player")

    def add_player(self):
        if len(self.players) >= 24:
            messagebox.showwarning("تنبيه", "الحد الأقصى 24 لاعب")
            return
        img_path = filedialog.askopenfilename(title="اختر صورة اللاعب", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not img_path: return
        name = simpledialog.askstring("اسم اللاعب", "أدخل اسم اللاعب:")
        if not name: return
        
        pid = len(self.players)
        self.players.append(Player(pid, name, img_path, pid + 1))
        self.draw_setup_players()

    def start_game(self):
        if len(self.players) < 2:
            messagebox.showwarning("تنبيه", "يجب إضافة لاعبين على الأقل")
            return
        self.slots = [p.original_slot for p in self.players]
        self.slots.append(len(self.slots) + 1) # Slot فارغ إضافي للحركة
        self.set_new_bomb()
        self.show_game_screen()

    # ================= شاشة اللعب الرئيسية =================
    def set_new_bomb(self):
        available = [s for s in self.slots if s != self.bomb_slot]
        self.bomb_slot = random.choice(available)

    def show_game_screen(self):
        self.clear_canvas()
        
        # الهيدر العلوي
        header = f"الدورة: {self.cycle}   |   الجولة: {self.round} / 3"
        self.create_rounded_rect(350, 20, 850, 80, radius=20, fill=PANEL_COLOR)
        self.canvas.create_text(600, 50, text=header, fill="#f1c40f", font=("Arial", 22, "bold"))
        
        self.draw_slots()
        self.handle_turn()

    def draw_slots(self):
        x_start = max((1200 - (len(self.slots) * 140)) / 2, 50) # توسيط الأماكن
        y = 200
        
        for i, slot in enumerate(self.slots):
            if i > 0 and i % 8 == 0:
                y += 180
                x_start = max((1200 - (min(len(self.slots)-i, 8) * 140)) / 2, 50)
                
            x = x_start + ((i % 8) * 140)
            
            # رسم الـ Slot
            self.create_rounded_rect(x, y, x+110, y+140, radius=15, fill=SLOT_COLOR)
            self.canvas.create_text(x+55, y+20, text=f"Slot {slot}", fill="#89c4f4", font=("Arial", 12, "bold"))
            
            # البحث عن اللاعب في هذا المكان
            player_in_slot = next((p for p in self.players if p.current_slot == slot), None)
            if player_in_slot:
                img = player_in_slot.img_normal
                if not player_in_slot.is_alive:
                    img = player_in_slot.img_dead
                
                img_id = self.canvas.create_image(x+10, y+35, anchor="nw", image=img)
                self.canvas.create_text(x+55, y+155, text=player_in_slot.name, fill=TEXT_COLOR if player_in_slot.is_alive else "gray", font=("Arial", 12))
                
                # جعل اللاعب الحي قابلاً للنقر (إذا أردنا التبديل معه)
                if player_in_slot.is_alive:
                    self.canvas.tag_bind(img_id, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                    self.canvas.tag_bind(img_id, "<Leave>", lambda e: self.canvas.config(cursor=""))
                    self.canvas.tag_bind(img_id, "<Button-1>", lambda e, target=player_in_slot: self.on_target_click(target))

    def handle_turn(self):
        # البحث عن اللاعب الذي لم يتخذ قراره
        alive_players = [p for p in self.players if p.is_alive]
        if len(alive_players) <= 1:
            self.end_game(alive_players)
            return

        current_player = next((p for p in alive_players if p.decision is None), None)
        
        decisions_made = len([p for p in alive_players if p.decision is not None])
        self.canvas.create_text(1050, 50, text=f"تم تسجيل قرارات: {decisions_made}/{len(alive_players)}", fill="#bdc3c7", font=("Arial", 14))

        if current_player:
            self.draw_control_panel(current_player)
        else:
            # اكتملت القرارات، عرض زر تنفيذ الحركة
            self.draw_button(450, 650, 300, 60, "⚡ تنفيذ الحركة المتزامنة ⚡", ACCENT_COLOR, "resolve_btn")
            self.canvas.tag_bind("resolve_btn", "<Button-1>", lambda e: self.resolve_round())

    def draw_control_panel(self, player):
        # اللوحة السفلية الخاصة بدور اللاعب
        panel_y = 600
        self.create_rounded_rect(100, panel_y, 1100, 750, radius=20, fill=PANEL_COLOR)
        
        # إبراز صورة اللاعب الحالي
        self.canvas.create_image(130, panel_y+30, anchor="nw", image=player.img_highlight)
        self.canvas.create_text(250, panel_y+75, text=f"حان دور: {player.name}", fill=TEXT_COLOR, font=("Arial", 20, "bold"), anchor="w")
        
        # أزرار القرارات
        self.draw_button(500, panel_y+40, 220, 60, "STAY - البقاء", BTN_STAY, "stay_btn")
        self.canvas.tag_bind("stay_btn", "<Button-1>", lambda e: self.register_decision(player, "STAY"))
        
        home_text = f"HOME - مكانك الأصلي ({player.original_slot})"
        self.draw_button(750, panel_y+40, 300, 60, home_text, BTN_HOME, "home_btn")
        self.canvas.tag_bind("home_btn", "<Button-1>", lambda e: self.register_decision(player, "HOME"))
        
        # نص إرشادي
        self.canvas.create_text(600, panel_y+130, text="لأخذ مكان لاعب آخر والتناوب معه: انقر على صورته مباشرة في الشاشة فوق 👆", fill="#89c4f4", font=("Arial", 14))

        self.current_turn_player = player # حفظ اللاعب الحالي للتحقق عند النقر

    def on_target_click(self, target_player):
        # المستخدم قام بالنقر على صورة لاعب في الشاشة
        if not hasattr(self, 'current_turn_player') or not self.current_turn_player: return
        p = self.current_turn_player
        
        if target_player.pid == p.pid:
            messagebox.showinfo("تنبيه", "لا يمكنك أخذ مكان نفسك! اختر البقاء (STAY) بدلاً من ذلك.")
            return
            
        # تسجيل القرار بأخذ مكان هذا اللاعب
        self.register_decision(p, target_player.pid)

    def register_decision(self, player, decision):
        player.decision = decision
        self.current_turn_player = None
        self.show_game_screen() # تحديث الشاشة للاعب التالي

    # ================= حل التعارضات وتحديث الأماكن =================
    def resolve_round(self):
        target_slots = {}
        # 1. تحديد الوجهة لكل لاعب
        for p in self.players:
            if not p.is_alive: continue
            target = p.current_slot
            if p.decision == "STAY": target = p.current_slot
            elif p.decision == "HOME": target = p.original_slot
            else: # النقر على لاعب آخر
                t_player = next(tp for tp in self.players if tp.pid == p.decision)
                target = t_player.current_slot
            target_slots[p.pid] = target

        # 2. فحص التعارض (أكثر من لاعب يريدون نفس الـ Slot)
        slot_counts = {}
        for pid, slot in target_slots.items():
            slot_counts[slot] = slot_counts.get(slot, 0) + 1

        # 3. التطبيق المتزامن
        for p in self.players:
            if not p.is_alive: continue
            wanted_slot = target_slots[p.pid]
            # إذا لم يكن هناك تعارض، ينتقل. إذا كان هناك تعارض، يبقى في مكانه (يتم تجاهل الحركة)
            if slot_counts[wanted_slot] <= 1:
                p.current_slot = wanted_slot
            
            p.decision = None # تصفير القرار للجولة القادمة
            
        if self.round == 3:
            self.reveal_bomb()
        else:
            self.round += 1
            self.show_game_screen()

    # ================= الكشف عن القنبلة =================
    def reveal_bomb(self):
        self.clear_canvas()
        self.canvas.create_text(600, 60, text="🔥 لحظة الحقيقة! كشف القنبلة 🔥", fill=ACCENT_COLOR, font=("Arial", 32, "bold"))
        
        self.draw_slots()
        
        # رسم تأثير القنبلة على المكان المحدد
        x_start = max((1200 - (len(self.slots) * 140)) / 2, 50)
        y = 200
        for i, slot in enumerate(self.slots):
            if i > 0 and i % 8 == 0:
                y += 180
                x_start = max((1200 - (min(len(self.slots)-i, 8) * 140)) / 2, 50)
            x = x_start + ((i % 8) * 140)
            
            if slot == self.bomb_slot:
                self.create_rounded_rect(x-5, y-5, x+115, y+145, radius=15, fill="", outline="red", width=5)
                self.canvas.create_text(x+55, y-25, text="💣 هنا القنبلة", fill="red", font=("Arial", 16, "bold"))

        # تحديد الضحية
        eliminated = None
        for p in self.players:
            if p.is_alive and p.current_slot == self.bomb_slot:
                p.is_alive = False
                eliminated = p
                
        panel_y = 600
        self.create_rounded_rect(200, panel_y, 1000, 720, radius=20, fill=PANEL_COLOR)
        
        if eliminated:
            msg = f"انفجرت القنبلة في {eliminated.name} وتم استبعاده!"
            color = "#e74c3c"
        else:
            msg = "المكان كان فارغاً! نجا الجميع في هذه الدورة."
            color = "#2ecc71"
            
        self.canvas.create_text(600, panel_y+60, text=msg, fill=color, font=("Arial", 24, "bold"))
        
        self.draw_button(500, panel_y+130, 200, 50, "بدء الدورة القادمة", "#3498db", "next_cycle_btn")
        self.canvas.tag_bind("next_cycle_btn", "<Button-1>", lambda e: self.next_cycle())

    def next_cycle(self):
        self.round = 1
        self.cycle += 1
        self.set_new_bomb()
        self.show_game_screen()

    def end_game(self, winners):
        self.clear_canvas()
        self.canvas.create_text(600, 200, text="🏆 انتهت اللعبة! 🏆", fill="#f1c40f", font=("Arial", 50, "bold"))
        
        if len(winners) == 1:
            winner = winners[0]
            self.canvas.create_image(550, 300, anchor="nw", image=winner.img_highlight)
            self.canvas.create_text(600, 450, text=f"الناجي الأخير: {winner.name}", fill=TEXT_COLOR, font=("Arial", 30, "bold"))
        else:
            self.canvas.create_text(600, 400, text="لا يوجد ناجين!", fill="red", font=("Arial", 30, "bold"))

if __name__ == "__main__":
    app = BombDodgeGame()
    app.mainloop()

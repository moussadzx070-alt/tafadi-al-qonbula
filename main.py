import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import random
import copy

class Player:
    def __init__(self, pid, name, image_path, original_slot):
        self.pid = pid
        self.name = name
        self.original_slot = original_slot
        self.current_slot = original_slot
        self.is_alive = True
        self.image = self.create_circular_image(image_path)
        self.decision = None # "STAY", "HOME", target_pid
        
    def create_circular_image(self, path, size=(80, 80)):
        try:
            img = Image.open(path).resize(size).convert("RGBA")
        except:
            # Fallback if image fails
            img = Image.new("RGBA", size, (200, 200, 200, 255))
        
        # Create circular mask
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Apply mask
        img.putalpha(mask)
        return ImageTk.PhotoImage(img)

class BombDodgeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("تفادي القنبلة - Bomb Dodge")
        self.geometry("1000x700")
        self.configure(bg="#2c3e50")
        
        self.players = []
        self.slots = []
        self.bomb_slot = -1
        self.round = 1
        self.cycle = 1
        self.decisions_made = 0
        
        self.show_setup_screen()

    def show_setup_screen(self):
        self.clear_screen()
        tk.Label(self, text="إعداد اللاعبين (2 إلى 24 لاعب)", font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
        
        self.players_frame = tk.Frame(self, bg="#2c3e50")
        self.players_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(self, bg="#2c3e50")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="إضافة لاعب (صورة + اسم)", command=self.add_player, font=("Arial", 14), bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="بدء اللعبة", command=self.start_game, font=("Arial", 14), bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=10)
        
        self.update_players_display()

    def add_player(self):
        if len(self.players) >= 24:
            messagebox.showwarning("تنبيه", "الحد الأقصى 24 لاعب")
            return
            
        img_path = filedialog.askopenfilename(title="اختر صورة اللاعب", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not img_path: return
        
        name = simpledialog.askstring("اسم اللاعب", "أدخل اسم اللاعب:")
        if not name: return
        
        pid = len(self.players)
        slot_id = pid + 1
        new_player = Player(pid, name, img_path, slot_id)
        self.players.append(new_player)
        self.update_players_display()

    def update_players_display(self):
        for widget in self.players_frame.winfo_children():
            widget.destroy()
            
        for p in self.players:
            frame = tk.Frame(self.players_frame, bg="#34495e", padx=10, pady=10)
            frame.pack(side=tk.LEFT, padx=10, pady=10)
            tk.Label(frame, image=p.image, bg="#34495e").pack()
            tk.Label(frame, text=p.name, font=("Arial", 12), bg="#34495e", fg="white").pack()

    def start_game(self):
        if len(self.players) < 2:
            messagebox.showwarning("تنبيه", "يجب إضافة لاعبين على الأقل")
            return
            
        self.slots = [p.original_slot for p in self.players]
        # إضافة سلوت إضافي فارغ لزيادة الحركة
        self.slots.append(len(self.slots) + 1) 
        
        self.set_new_bomb()
        self.show_game_screen()

    def set_new_bomb(self):
        available_slots = [s for s in self.slots if s != self.bomb_slot]
        self.bomb_slot = random.choice(available_slots)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_game_screen(self):
        self.clear_screen()
        
        header = f"الدورة: {self.cycle} | الجولة: {self.round}/3"
        tk.Label(self, text=header, font=("Arial", 20, "bold"), bg="#2c3e50", fg="#f1c40f").pack(pady=10)
        
        # Slots Display
        self.canvas = tk.Canvas(self, width=900, height=400, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.draw_slots()
        
        # Controls
        self.control_frame = tk.Frame(self, bg="#2c3e50")
        self.control_frame.pack(pady=10, fill=tk.X)
        self.setup_decision_ui()

    def draw_slots(self):
        self.canvas.delete("all")
        x_offset = 50
        y_offset = 150
        spacing = 150
        
        for idx, slot in enumerate(self.slots):
            x = x_offset + (idx % 6) * spacing
            y = y_offset + (idx // 6) * 150
            
            # Draw Slot
            self.canvas.create_rectangle(x, y, x+100, y+100, outline="white", width=2)
            self.canvas.create_text(x+50, y-20, text=f"Slot {slot}", fill="white", font=("Arial", 12))
            
            # Draw Player in this slot (if any)
            for p in self.players:
                if p.current_slot == slot:
                    # Draw circular image
                    img_id = self.canvas.create_image(x+10, y+10, anchor=tk.NW, image=p.image)
                    if not p.is_alive:
                        # Gray out if dead (simulated via text)
                        self.canvas.create_text(x+50, y+50, text="X", fill="red", font=("Arial", 40, "bold"))
                    self.canvas.create_text(x+50, y+110, text=p.name, fill="white" if p.is_alive else "gray", font=("Arial", 10))

    def setup_decision_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
            
        alive_players = [p for p in self.players if p.is_alive]
        if len(alive_players) <= 1:
            self.end_game(alive_players)
            return

        tk.Label(self.control_frame, text=f"القرارات المسجلة: {self.decisions_made} / {len(alive_players)}", font=("Arial", 14), bg="#2c3e50", fg="white").pack()
        
        # Find next player who hasn't decided
        current_player = next((p for p in alive_players if p.decision is None), None)
        
        if current_player:
            frame = tk.Frame(self.control_frame, bg="#34495e", padx=20, pady=20)
            frame.pack(pady=10)
            tk.Label(frame, text=f"دور اللاعب: {current_player.name}", font=("Arial", 16, "bold"), bg="#34495e", fg="#3498db").pack(pady=10)
            
            tk.Button(frame, text="STAY - البقاء", command=lambda: self.make_decision(current_player, "STAY"), width=20, bg="#2980b9", fg="white").pack(pady=5)
            tk.Button(frame, text="HOME - العودة للأصل", command=lambda: self.make_decision(current_player, "HOME"), width=20, bg="#27ae60", fg="white").pack(pady=5)
            
            for target in alive_players:
                if target != current_player:
                    tk.Button(frame, text=f"MOVE TO -> {target.name}", command=lambda t=target: self.make_decision(current_player, t.pid), width=20).pack(pady=2)
        else:
            tk.Button(self.control_frame, text="تنفيذ الحركة المتزامنة", command=self.resolve_round, font=("Arial", 16, "bold"), bg="#e67e22", fg="white").pack(pady=20)

    def make_decision(self, player, decision):
        player.decision = decision
        self.decisions_made += 1
        self.setup_decision_ui()

    def resolve_round(self):
        # 1. Map target slots
        target_slots = {}
        for p in self.players:
            if not p.is_alive: continue
            
            target = p.current_slot
            if p.decision == "STAY":
                target = p.current_slot
            elif p.decision == "HOME":
                target = p.original_slot
            else: # Move to player
                target_player = next(tp for tp in self.players if tp.pid == p.decision)
                target = target_player.current_slot
                
            target_slots[p.pid] = target

        # 2. Find conflicts (slots targeted by >1 player)
        slot_counts = {}
        for pid, slot in target_slots.items():
            slot_counts[slot] = slot_counts.get(slot, 0) + 1

        # 3. Apply moves
        for p in self.players:
            if not p.is_alive: continue
            wanted_slot = target_slots[p.pid]
            # If conflict, stay in current slot, else move
            if slot_counts[wanted_slot] > 1:
                pass # Conflict! Movement canceled.
            else:
                p.current_slot = wanted_slot
            
            p.decision = None # Reset decision
            
        self.decisions_made = 0
        
        if self.round == 3:
            self.reveal_bomb()
        else:
            self.round += 1
            self.show_game_screen()

    def reveal_bomb(self):
        self.clear_screen()
        tk.Label(self, text="الكشف عن القنبلة!", font=("Arial", 30, "bold"), bg="#2c3e50", fg="#e74c3c").pack(pady=30)
        
        self.canvas = tk.Canvas(self, width=900, height=400, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.draw_slots()
        
        # Highlight bomb slot
        for idx, slot in enumerate(self.slots):
            if slot == self.bomb_slot:
                x = 50 + (idx % 6) * 150
                y = 150 + (idx // 6) * 150
                self.canvas.create_rectangle(x, y, x+100, y+100, outline="red", width=5)
                self.canvas.create_text(x+50, y-40, text="💣 القنبلة هنا", fill="red", font=("Arial", 16, "bold"))
        
        # Eliminate player if in bomb slot
        eliminated = None
        for p in self.players:
            if p.is_alive and p.current_slot == self.bomb_slot:
                p.is_alive = False
                eliminated = p
                
        msg = f"تم استبعاد: {eliminated.name}" if eliminated else "نجا الجميع هذه الدورة!"
        tk.Label(self, text=msg, font=("Arial", 20), bg="#2c3e50", fg="white").pack(pady=20)
        
        tk.Button(self, text="متابعة إلى الدورة القادمة", command=self.next_cycle, font=("Arial", 16), bg="#3498db", fg="white").pack(pady=20)

    def next_cycle(self):
        self.round = 1
        self.cycle += 1
        self.set_new_bomb()
        self.show_game_screen()

    def end_game(self, winners):
        self.clear_screen()
        winner_name = winners[0].name if len(winners) == 1 else "لا أحد (تعادل)"
        tk.Label(self, text="انتهت اللعبة!", font=("Arial", 40, "bold"), bg="#2c3e50", fg="#f1c40f").pack(pady=50)
        tk.Label(self, text=f"الفائز: {winner_name}", font=("Arial", 30), bg="#2c3e50", fg="white").pack(pady=20)
        
        if winners:
            tk.Label(self, image=winners[0].image, bg="#2c3e50").pack()

if __name__ == "__main__":
    app = BombDodgeGame()
    app.mainloop()

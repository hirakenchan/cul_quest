import pyxel
import random
import PyxelUniversalFont as puf

writer = puf.Writer("misaki_gothic.ttf")


class App:
    def __init__(self):
        self.fps = 30
        pyxel.init(256, 192, title="Math Quest", fps=self.fps)

        # 画像サイズ
        self.sprite_size = 38

        # 画像読み込み
        # キャラクターは38×38 前提
        pyxel.images[0].load(0, 0, "hero.png")
        pyxel.images[1].load(0, 0, "slime.png")

        # 画像バンク2に横並びで読み込み
        pyxel.images[2].load(0, 0, "ghost.png")      # 38×38
        pyxel.images[2].load(48, 0, "gorem.png")     # 44×44
        pyxel.images[2].load(96, 0, "dragon.png")    # 56×56

        self.player_max_hp = 5

        # モンスター情報
        self.monsters = [
            {
                "name": "スライム",
                "image_bank": 1,
                "image_x": 0,
                "image_y": 0,
                "image_w": 38,
                "image_h": 38,
                "draw_x": 50,
                "draw_y": 42,
                "name_x": 52,
                "name_y": 80,
                "max_hp": 5,
            },
            {
                "name": "ゴースト",
                "image_bank": 2,
                "image_x": 0,
                "image_y": 0,
                "image_w": 38,
                "image_h": 38,
                "draw_x": 50,
                "draw_y": 42,
                "name_x": 52,
                "name_y": 80,
                "max_hp": 8,
            },
            {
                "name": "ゴーレム",
                "image_bank": 2,
                "image_x": 48,
                "image_y": 0,
                "image_w": 44,
                "image_h": 44,
                "draw_x": 47,
                "draw_y": 38,
                "name_x": 52,
                "name_y": 82,
                "max_hp": 10,
            },
            {
                "name": "ドラゴン",
                "image_bank": 2,
                "image_x": 96,
                "image_y": 0,
                "image_w": 56,
                "image_h": 56,
                "draw_x": 40,
                "draw_y": 26,
                "name_x": 52,
                "name_y": 82,
                "max_hp": 18,
            },
        ]

        self.current_monster_index = 0
        self.monster_max_hp = self.monsters[self.current_monster_index]["max_hp"]

        self.player_hp = self.player_max_hp
        self.monster_hp = self.monster_max_hp
        self.score = 0
        self.message = ""
        self.message_color = 7
        self.input_text = ""

        # 制限時間
        self.time_limit_sec = 20
        self.time_limit = self.time_limit_sec * self.fps
        self.time_left = self.time_limit

        # 時間切れ後の待機
        self.time_up_waiting = False
        self.time_up_timer = 0

        # モンスター撃破状態
        self.monster_defeated = False
        self.defeat_timer = 0
        self.defeated_monster_name = ""

        # プレイヤー敗北状態
        self.player_defeated = False
        self.game_over_timer = 0

        # 攻撃アニメーション
        self.attack_animating = False
        self.attack_timer = 0
        self.attack_total_frames = 14
        self.attack_hit_done = False
        self.hero_attack_dx = 0
        self.monster_shake_x = 0
        self.pending_monster_defeat = False

        # モンスター攻撃アニメーション
        self.monster_attack_animating = False
        self.monster_attack_timer = 0
        self.monster_attack_total_frames = 14
        self.monster_attack_hit_done = False
        self.monster_attack_dx = 0
        self.hero_shake_x = 0
        self.pending_player_defeat = False

        # 入力パッドを中央寄せ
        self.button_w = 48
        self.button_h = 16
        self.buttons = [
            ("7", 24, 116), ("8", 104, 116), ("9", 184, 116),
            ("4", 24, 136), ("5", 104, 136), ("6", 184, 136),
            ("1", 24, 156), ("2", 104, 156), ("3", 184, 156),
            ("C", 24, 176), ("0", 104, 176), ("OK", 184, 176),
        ]

        self.make_question()
        pyxel.run(self.update, self.draw)

    def make_question(self):
        op = random.choice(["+", "-", "x"])

        if op == "+":
            self.a = random.randint(1, 20)
            self.b = random.randint(1, 20)
            self.answer = self.a + self.b

        elif op == "-":
            self.a = random.randint(1, 20)
            self.b = random.randint(1, 20)
            if self.a < self.b:
                self.a, self.b = self.b, self.a
            self.answer = self.a - self.b

        else:
            self.a = random.randint(1, 9)
            self.b = random.randint(1, 9)
            self.answer = self.a * self.b

        self.op = op
        self.input_text = ""
        self.time_left = self.time_limit
    
    def next_monster(self):
        self.current_monster_index += 1

        # 最後まで行ったら最初に戻る
        if self.current_monster_index >= len(self.monsters):
            self.current_monster_index = 0

        self.monster_max_hp = self.monsters[self.current_monster_index]["max_hp"]
        self.monster_hp = self.monster_max_hp

    def update(self):
        # プレイヤー敗北中なら入力を止める
        if self.player_defeated:
            self.game_over_timer -= 1

            if self.game_over_timer <= 0:
                self.player_defeated = False
                self.player_hp = self.player_max_hp

                self.current_monster_index = 0
                self.monster_max_hp = self.monsters[self.current_monster_index]["max_hp"]
                self.monster_hp = self.monster_max_hp

                self.score = 0
                self.message = ""
                self.input_text = ""
                self.make_question()

            return

        # モンスター撃破中なら入力を止める
        if self.monster_defeated:
            self.defeat_timer -= 1

            if self.defeat_timer <= 0:
                self.monster_defeated = False
                self.next_monster()
                self.message = ""
                self.input_text = ""
                self.make_question()

            return

        # 攻撃アニメーション中なら入力を止める
        if self.attack_animating:
            self.update_attack_animation()
            return
        
        # モンスター攻撃アニメーション中なら入力を止める
        if self.monster_attack_animating:
            self.update_monster_attack_animation()
            return

        # 時間切れ表示中の待機時間
        if self.time_up_waiting:
            self.time_up_timer -= 1

            if self.time_up_timer <= 0:
                self.time_up_waiting = False
                self.message = ""

                # HPが0ならGAME OVERへ
                if self.player_hp <= 0:
                    self.player_defeated = True
                    self.game_over_timer = 90
                    return

                # HPが残っていれば次の問題へ
                self.make_question()

            return

        # 制限時間を減らす
        self.time_left -= 1

        # 時間切れ
        if self.time_left <= 0:
            self.time_up()
            return

        # キーボード入力
        for i in range(10):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                self.input_text += str(i)

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.input_text = self.input_text[:-1]

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.check_answer()

        # マウスクリック
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y

            for label, x, y in self.buttons:
                if x <= mx <= x + self.button_w and y <= my <= y + self.button_h:
                    self.press_button(label)

    def press_button(self, label):
        if label == "C":
            self.input_text = ""
        elif label == "OK":
            self.check_answer()
        else:
            self.input_text += label

    def check_answer(self):
        if self.input_text == "":
            self.message = ""
            self.message_color = 10
            return

        if int(self.input_text) == self.answer:
            self.input_text = ""
            self.start_hero_attack()
            return

        else:
            self.input_text = ""
            self.start_monster_attack()
            return

    def start_hero_attack(self):
        self.attack_animating = True
        self.attack_timer = self.attack_total_frames
        self.attack_hit_done = False
        self.hero_attack_dx = 0
        self.monster_shake_x = 0
        self.pending_monster_defeat = False

        self.message = "せいかい！"
        self.message_color = 8
    
    def start_monster_attack(self):
        self.monster_attack_animating = True
        self.monster_attack_timer = self.monster_attack_total_frames
        self.monster_attack_hit_done = False

        self.monster_attack_dx = 0
        self.hero_shake_x = 0
        self.pending_player_defeat = False

        self.message = "まちがい！"
        self.message_color = 12


    def update_monster_attack_animation(self):
        frame = self.monster_attack_total_frames - self.monster_attack_timer

        # モンスターが少し右へ出る → 少し止まる → 戻る
        if frame <= 3:
            self.monster_attack_dx = frame * 3
        elif frame <= 7:
            self.monster_attack_dx = 9
        else:
            self.monster_attack_dx = max(0, 9 - (frame - 7) * 3)

        # 勇者を少し揺らす
        if frame in [5, 6, 7]:
            self.hero_shake_x = -2 if frame % 2 == 1 else 2
        else:
            self.hero_shake_x = 0

        # ヒット判定は1回だけ
        if frame >= 6 and not self.monster_attack_hit_done:
            self.monster_attack_hit_done = True
            self.player_hp -= 1

            if self.player_hp <= 0:
                self.pending_player_defeat = True

        self.monster_attack_timer -= 1

        # アニメーション終了
        if self.monster_attack_timer <= 0:
            self.monster_attack_animating = False
            self.monster_attack_dx = 0
            self.hero_shake_x = 0

            if self.pending_player_defeat:
                self.message = ""
                self.player_defeated = True
                self.game_over_timer = 90
                self.input_text = ""
            else:
                self.message = ""
                self.make_question()

    def update_attack_animation(self):
        frame = self.attack_total_frames - self.attack_timer

        # 勇者が少し左へ出る → 少し止まる → 戻る
        if frame <= 3:
            self.hero_attack_dx = -frame * 3
        elif frame <= 7:
            self.hero_attack_dx = -9
        else:
            self.hero_attack_dx = min(0, -9 + (frame - 7) * 3)

        # モンスターを少し揺らす
        if frame in [5, 6, 7]:
            self.monster_shake_x = -2 if frame % 2 == 1 else 2
        else:
            self.monster_shake_x = 0

        # ヒット判定は1回だけ
        if frame >= 6 and not self.attack_hit_done:
            self.attack_hit_done = True
            self.monster_hp -= 1
            self.score += 1

            if self.monster_hp <= 0:
                current_monster = self.monsters[self.current_monster_index]
                self.defeated_monster_name = current_monster["name"]
                self.pending_monster_defeat = True

        self.attack_timer -= 1

        # アニメーション終了
        if self.attack_timer <= 0:
            self.attack_animating = False
            self.hero_attack_dx = 0
            self.monster_shake_x = 0

            if self.pending_monster_defeat:
                self.message = ""
                self.monster_defeated = True
                self.defeat_timer = 90
                self.input_text = ""
            else:
                self.message = ""
                self.make_question()

    def time_up(self):
        self.message = "じかんぎれ！"
        self.message_color = 12
        self.player_hp -= 1
        self.input_text = ""

        # タイマーは0で止める
        self.time_left = 0

        # 1秒待機
        self.time_up_waiting = True
        self.time_up_timer = self.fps

    def draw(self):
        pyxel.cls(0)

        self.draw_status()
        self.draw_time_text()
        self.draw_battle_area()
        self.draw_question_area()

        # 区切り線
        pyxel.line(0, 108, 256, 108, 7)

        self.draw_keypad()

    def draw_text(self, x, y, text, size=8, color=7):
        writer.draw(x, y, text, size, color)

    def draw_center_text(self, x, y, w, text, size=8, color=7):
        text_width = len(text) * size
        draw_x = x + (w - text_width) // 2
        writer.draw(draw_x, y, text, size, color)

    def draw_battle_area(self):
        monster_x = 50 + self.monster_shake_x + self.monster_attack_dx
        monster_y = 42

        hero_x = 158 + self.hero_attack_dx + self.hero_shake_x
        hero_y = 40

        # モンスター側
        if self.monster_defeated:
            defeated_name = self.defeated_monster_name or "モンスター"
            self.draw_center_text(20, 42, 110, defeated_name + "を", 8, 10)
            self.draw_center_text(20, 55, 110, "たおした！！", 8, 10)
        else:
            current_monster = self.monsters[self.current_monster_index]

            monster_x = current_monster["draw_x"] + self.monster_shake_x + self.monster_attack_dx
            monster_y = current_monster["draw_y"]

            pyxel.blt(
                monster_x,
                monster_y,
                current_monster["image_bank"],
                current_monster["image_x"],
                current_monster["image_y"],
                current_monster["image_w"],
                current_monster["image_h"],
                0
            )

            self.draw_text(
                current_monster["name_x"],
                current_monster["name_y"],
                current_monster["name"],
                8,
                7
            )

            self.draw_text(52, 80, current_monster["name"], 8, 7)

        # 勇者側
        if self.player_defeated:
            self.draw_center_text(170, 45, 90, "GAME OVER ..", 8, 8)
        else:
            pyxel.blt(
                hero_x,
                hero_y,
                0,  # 勇者は画像バンク0
                0,
                0,
                self.sprite_size,
                self.sprite_size,
                0
            )
            self.draw_text(160, 80, "ゆうしゃ", 8, 7)

        # 勇者攻撃中：モンスター側に斜線エフェクト
        if self.attack_animating:
            frame = self.attack_total_frames - self.attack_timer

            if frame in [5, 6, 7]:
                pyxel.line(96, 46, 80, 64, 7)
                pyxel.line(98, 46, 82, 64, 10)

        # モンスター攻撃中：勇者側に斜線エフェクト
        if self.monster_attack_animating:
            frame = self.monster_attack_total_frames - self.monster_attack_timer

            if frame in [5, 6, 7]:
                pyxel.line(168, 46, 184, 62, 12)
                pyxel.line(170, 46, 186, 62, 7)

    def draw_status(self):
        # 左：モンスターHP
        if not self.monster_defeated:
            self.draw_text(18, 8, "HP", 8, 8)
            self.draw_hp_bar(28, 7, 60, 8, self.monster_hp, self.monster_max_hp, 8)

        # 中央：スコア
        self.draw_center_text(100, 8, 56, f"{self.score}ポイント", 8, 7)

        # 右：勇者HP
        if not self.player_defeated:
            self.draw_text(178, 8, "HP", 8, 11)
            self.draw_hp_bar(188, 7, 60, 8, self.player_hp, self.player_max_hp, 11)

    def draw_time_text(self):
        seconds_left = max(0, (self.time_left + self.fps - 1) // self.fps)

        # 位置はいったん中央上
        self.draw_text(96, 20, f"のこりじかん： {seconds_left}", 8, 10)

    def draw_hp_bar(self, x, y, width, height, hp, max_hp, color):
        pyxel.rectb(x, y, width, height, 7)
        pyxel.rect(x + 1, y + 1, width - 2, height - 2, 0)

        hp_width = int((width - 2) * hp / max_hp)
        if hp_width > 0:
            pyxel.rect(x + 1, y + 1, hp_width, height - 2, color)

    def draw_question_area(self):
        question = f"{self.a} {self.op} {self.b} = ？"
        answer_text = self.input_text if self.input_text != "" else "_"

        # 問題欄を広めに確保
        pyxel.rect(40, 90, 180, 14, 1)
        pyxel.rectb(40, 90, 180, 14, 7)

        # 左：問題
        self.draw_text(58, 93, question, 8, 7)

        # 右：こたえ
        self.draw_text(150, 93, "こたえ:", 8, 10)

        # 答え表示枠
        self.draw_text(180, 93, answer_text, 8, 10)

        # メッセージは中央に小さく表示
        if self.message:
            self.draw_text(108, 72, self.message, 8, self.message_color)

    def draw_keypad(self):
        for label, x, y in self.buttons:
            pyxel.rect(x, y, self.button_w, self.button_h, 5)
            pyxel.rectb(x, y, self.button_w, self.button_h, 7)

            if label in ["C", "OK"]:
                self.draw_center_text(x, y + 4, self.button_w, label, 8, 7)
            else:
                pyxel.text(x + 21, y + 5, label, 7)


App()
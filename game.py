import pyxel
import random
import PyxelUniversalFont as puf

writer = puf.Writer("misaki_gothic.ttf")


class App:
    def __init__(self):
        self.fps = 30
        pyxel.init(256, 192, title="Math Quest", fps=self.fps)

        self.player_max_hp = 5
        self.monster_max_hp = 5

        self.player_hp = self.player_max_hp
        self.monster_hp = self.monster_max_hp
        self.score = 0
        self.message = ""
        self.message_color = 7
        self.input_text = ""

        # 制限時間
        self.time_limit_sec = 10  # 秒数
        self.time_limit = self.time_limit_sec * self.fps
        self.time_left = self.time_limit

        # 時間切れ後の待機
        self.time_up_waiting = False
        self.time_up_timer = 0

        self.monster_defeated = False
        self.defeat_timer = 0

        self.player_defeated = False
        self.game_over_timer = 0

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

        # 問題が変わるたびに制限時間を戻す
        self.time_left = self.time_limit

    def update(self):
        # プレイヤー敗北中なら入力を止める
        if self.player_defeated:
            self.game_over_timer -= 1

            if self.game_over_timer <= 0:
                self.player_defeated = False
                self.player_hp = self.player_max_hp
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
                self.monster_hp = self.monster_max_hp
                self.message = ""
                self.input_text = ""
                self.make_question()

            return

        # 時間切れ表示中は1秒待つ
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
            self.message_color = 10  # 黄色
            return

        if int(self.input_text) == self.answer:
            self.message = "せいかい！"
            self.message_color = 8  # 赤色
            self.monster_hp -= 1
            self.score += 1

            if self.monster_hp <= 0:
                self.message = ""
                self.message_color = 10  # 黄色
                self.monster_defeated = True
                self.defeat_timer = 90
                self.input_text = ""
                return

            self.make_question()

        else:
            self.message = "まちがい！"
            self.message_color = 12  # 青色
            self.player_hp -= 1
            self.input_text = ""

            if self.player_hp <= 0:
                self.message = ""
                self.message_color = 8
                self.player_defeated = True
                self.game_over_timer = 90
                self.input_text = ""
                return
            
            self.make_question()
    
    def time_up(self):
        self.message = "じかんぎれ！"
        self.message_color = 12  # 青色
        self.player_hp -= 1
        self.input_text = ""

        # タイマーは0で止める
        self.time_left = 0

        # 1秒待機
        self.time_up_waiting = True
        self.time_up_timer = self.fps

        # HPがなくなったらゲームオーバー
        if self.player_hp <= 0:
            self.message = ""
            self.message_color = 8
            self.player_defeated = True
            self.game_over_timer = 90
            return

        # HPが残っていれば次の問題へ
        self.make_question()

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
        # モンスター側
        if self.monster_defeated:
            self.draw_center_text(20, 42, 110, "モンスターを", 8, 10)
            self.draw_center_text(20, 55, 110, "たおした！！", 8, 10)
        else:
            pyxel.circ(70, 48, 18, 12)
            pyxel.tri(52, 48, 70, 20, 88, 48, 12)
            pyxel.circ(63, 45, 2, 0)
            pyxel.circ(77, 45, 2, 0)
            pyxel.line(63, 58, 77, 58, 0)
            self.draw_text(50, 72, "モンスター", 8, 7)

        # 勇者側
        if self.player_defeated:
            self.draw_center_text(170, 45, 90, "GAME OVER ..", 8, 8)
        else:
            pyxel.rect(170, 40, 16, 24, 11)
            pyxel.rect(172, 28, 12, 12, 10)
            pyxel.rect(168, 52, 4, 18, 4)
            pyxel.rect(186, 52, 4, 18, 4)
            pyxel.line(190, 42, 205, 28, 7)
            self.draw_text(163, 72, "ゆうしゃ", 8, 7)

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
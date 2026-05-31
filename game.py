import pyxel
import random
import json
import os
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
        pyxel.images[2].load(0, 0, "ghost.png")       # 38×38
        pyxel.images[2].load(48, 0, "gorem.png")      # 46×46
        pyxel.images[2].load(104, 0, "dragon.png")    # 72×72

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
                "name_box_x": 30,
                "name_box_w": 80,
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
                "name_box_x": 30,
                "name_box_w": 80,
                "name_y": 80,
                "max_hp": 8,
            },
            {
                "name": "ゴーレム",
                "image_bank": 2,
                "image_x": 48,
                "image_y": 0,
                "image_w": 46,
                "image_h": 46,
                "draw_x": 45,
                "draw_y": 36,
                "name_y": 82,
                "max_hp": 10,
            },
            {
                "name": "ドラゴン",
                "image_bank": 2,
                "image_x": 104,
                "image_y": 0,
                "image_w": 72,
                "image_h": 72,
                "draw_x": 22,
                "draw_y": 12,
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

        # 画面状態
        self.scene = "title"
        self.selected_level_index = 0
        self.current_level = None

        # レベル情報
        self.levels = [
            {
                "name": "1. 1けた たしざん・ひきざん",
                "type": "one_digit_add_sub",
                "monster_index": 0,
            },
            {
                "name": "2. 2けた たしざん・ひきざん",
                "type": "two_digit_add_sub",
                "monster_index": 1,
            },
            {
                "name": "3. 1けた かけざん",
                "type": "one_digit_multiply",
                "monster_index": 2,
            },
            {
                "name": "4. かんたん わりざん",
                "type": "simple_divide",
                "monster_index": 3,
            },
        ]

        # トップ画面のボタン範囲
        self.ranking_button = {
            "x": 78,
            "y": 166,
            "w": 100,
            "h": 16,
        }

        # 問題数選択
        self.question_count_options = [5, 10, 20]
        self.selected_question_count_index = 1  # 最初は10問
        self.target_question_count = 10
        self.correct_count = 0

        # 結果表示用
        self.miss_count = 0
        self.elapsed_frames = 0

        # ランキング保存
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ranking_file = os.path.join(self.base_dir, "ranking.json")
        self.ranking_records = self.load_ranking()


        # ランキング設定
        self.max_ranking_count = 5
        self.pending_record = None

        # 名前入力
        self.player_name = ""
        self.max_name_length = 8

        # クリア結果用
        self.clear_time_sec = 0
        self.is_new_best = False
        
        # 問題数選択
        self.question_count_options = [5, 10, 20]
        self.selected_question_count_index = 1  # 最初は10問
        self.target_question_count = 10
        self.correct_count = 0

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

        pyxel.run(self.update, self.draw)

    def make_question(self):
        # まだレベルが選ばれていない場合は何もしない
        if self.current_level is None:
            return

        level_type = self.current_level["type"]

        if level_type == "one_digit_add_sub":
            op = random.choice(["+", "-"])
            self.a = random.randint(1, 9)
            self.b = random.randint(1, 9)

            if op == "+":
                self.answer = self.a + self.b
            else:
                if self.a < self.b:
                    self.a, self.b = self.b, self.a
                self.answer = self.a - self.b

        elif level_type == "two_digit_add_sub":
            op = random.choice(["+", "-"])
            self.a = random.randint(10, 49)
            self.b = random.randint(10, 49)

            if op == "+":
                self.answer = self.a + self.b
            else:
                if self.a < self.b:
                    self.a, self.b = self.b, self.a
                self.answer = self.a - self.b

        elif level_type == "one_digit_multiply":
            op = "x"
            self.a = random.randint(1, 9)
            self.b = random.randint(1, 9)
            self.answer = self.a * self.b

        elif level_type == "simple_divide":
            op = "÷"

            # 割り切れる問題だけ作る
            self.b = random.randint(2, 9)
            self.answer = random.randint(2, 9)
            self.a = self.b * self.answer

        self.op = op
        self.input_text = ""
        self.time_left = self.time_limit

    def load_ranking(self):
        if not os.path.exists(self.ranking_file):
            return {}

        try:
            with open(self.ranking_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        
    def save_ranking(self):
        with open(self.ranking_file, "w", encoding="utf-8") as f:
            json.dump(self.ranking_records, f, ensure_ascii=False, indent=2)

    def get_ranking_key(self):
        level_type = self.current_level["type"]
        return f"{level_type}_{self.target_question_count}"
    
    def save_best_record(self):
        ranking_key = self.get_ranking_key()

        new_record = {
            "level_name": self.current_level["name"],
            "level_type": self.current_level["type"],
            "question_count": self.target_question_count,
            "clear_time_sec": self.clear_time_sec,
            "miss_count": self.miss_count,
        }

        old_record = self.ranking_records.get(ranking_key)

        # まだ記録がない場合は保存
        if old_record is None:
            self.ranking_records[ranking_key] = new_record
            self.save_ranking()
            return True

        old_score = (
            old_record["clear_time_sec"],
            old_record["miss_count"],
        )

        new_score = (
            new_record["clear_time_sec"],
            new_record["miss_count"],
        )

        # 時間が短い、または同じ時間でミスが少なければ更新
        if new_score < old_score:
            self.ranking_records[ranking_key] = new_record
            self.save_ranking()
            return True

        return False
    
    def finish_stage(self):
        self.clear_time_sec = self.elapsed_frames // self.fps

        new_record = {
            "name": "",
            "level_name": self.current_level["name"],
            "level_type": self.current_level["type"],
            "question_count": self.target_question_count,
            "clear_time_sec": self.clear_time_sec,
            "miss_count": self.miss_count,
        }

        self.pending_record = new_record

        # ランキングに入るなら名前入力へ
        if self.can_enter_ranking(new_record):
            self.player_name = ""
            self.scene = "name_input"
        else:
            # 入らないならそのままランキング表示
            self.pending_record = None
            self.scene = "ranking"
    
    def next_monster(self):
        self.current_monster_index += 1

        # 最後まで行ったら最初に戻る
        if self.current_monster_index >= len(self.monsters):
            self.current_monster_index = 0

        self.monster_max_hp = self.monsters[self.current_monster_index]["max_hp"]
        self.monster_hp = self.monster_max_hp

    def update_battle(self):
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
                self.message = ""
                self.input_text = ""
                self.finish_stage()

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
        
        # プレイ時間をカウント
        self.elapsed_frames += 1

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
    
    def update_clear(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.message = ""
            self.input_text = ""
            self.scene = "title"
    
    def update(self):
        if self.scene == "title":
            self.update_title()
        elif self.scene == "count_select":
            self.update_count_select()
        elif self.scene == "battle":
            self.update_battle()
        elif self.scene == "clear":
            self.update_clear()
        elif self.scene == "name_input":
            self.update_name_input()
        elif self.scene == "ranking":
            self.update_ranking()
    
    def update_title(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_level_index -= 1
            if self.selected_level_index < 0:
                self.selected_level_index = len(self.levels) - 1

        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_level_index += 1
            if self.selected_level_index >= len(self.levels):
                self.selected_level_index = 0

        for i in range(len(self.levels)):
            key = getattr(pyxel, f"KEY_{i + 1}")
            if pyxel.btnp(key):
                self.select_level(i)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.select_level(self.selected_level_index)

        # ランキングボタンをクリック
        if self.is_clicked(
            self.ranking_button["x"],
            self.ranking_button["y"],
            self.ranking_button["w"],
            self.ranking_button["h"]
        ):
            self.scene = "ranking"
    
    def update_count_select(self):
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_LEFT):
            self.selected_question_count_index -= 1
            if self.selected_question_count_index < 0:
                self.selected_question_count_index = len(self.question_count_options) - 1

        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_RIGHT):
            self.selected_question_count_index += 1
            if self.selected_question_count_index >= len(self.question_count_options):
                self.selected_question_count_index = 0

        for i in range(len(self.question_count_options)):
            key = getattr(pyxel, f"KEY_{i + 1}")
            if pyxel.btnp(key):
                self.selected_question_count_index = i
                self.start_level()

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.start_level()

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.scene = "title"

    def update_name_input(self):
        # A〜Z
        for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            key = getattr(pyxel, f"KEY_{ch}")
            if pyxel.btnp(key):
                if len(self.player_name) < self.max_name_length:
                    self.player_name += ch

        # 0〜9
        for i in range(10):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                if len(self.player_name) < self.max_name_length:
                    self.player_name += str(i)

        # 1文字消す
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.player_name = self.player_name[:-1]

        # 決定
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.save_pending_record()
            self.scene = "ranking"

    def update_ranking(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.message = ""
            self.input_text = ""
            self.scene = "title"

    def select_level(self, level_index):
        self.selected_level_index = level_index
        self.current_level = self.levels[level_index]

        # 問題数選択は毎回10問から開始
        self.selected_question_count_index = 1

        self.scene = "count_select"

        # 問題数選択は毎回10問から始める
        self.selected_question_count_index = 1

        self.scene = "count_select"
    
    def start_level(self):
        if self.current_level is None:
            return

        # 選んだ問題数
        self.target_question_count = self.question_count_options[
            self.selected_question_count_index
        ]

        # レベルに対応したモンスターをセット
        self.current_monster_index = self.current_level["monster_index"]

        # 問題数 = モンスターHP
        self.monster_max_hp = self.target_question_count

        # 状態をリセット
        self.player_hp = self.player_max_hp
        self.monster_hp = self.monster_max_hp
        self.score = 0
        self.correct_count = 0
        self.miss_count = 0
        self.elapsed_frames = 0

        self.message = ""
        self.message_color = 7
        self.input_text = ""

        self.monster_defeated = False
        self.player_defeated = False
        self.attack_animating = False
        self.monster_attack_animating = False
        self.time_up_waiting = False

        self.make_question()
        self.scene = "battle"

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
            self.correct_count += 1

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

        if self.scene == "title":
            self.draw_title()
        elif self.scene == "count_select":
            self.draw_count_select()
        elif self.scene == "battle":
            self.draw_battle()
        elif self.scene == "clear":
            self.draw_clear()
        elif self.scene == "name_input":
            self.draw_name_input()
        elif self.scene == "ranking":
            self.draw_ranking()

    def draw_battle(self):
        pyxel.cls(0)

        self.draw_status()
        self.draw_time_text()
        self.draw_battle_area()
        self.draw_question_area()

        # 区切り線
        pyxel.line(0, 108, 256, 108, 7)

        self.draw_keypad()
    
    def draw_title(self):
        # タイトル
        self.draw_center_text(0, 24, 256, "けいさんクエスト", 20, 7)

        # 説明
        self.draw_center_text(0, 48, 256, "レベルをえらんでね", 8, 10)

        # レベル一覧
        start_y = 72

        for i, level in enumerate(self.levels):
            y = start_y + i * 18

            if i == self.selected_level_index:
                # 選択中の行
                pyxel.rect(24, y - 2, 208, 14, 1)
                pyxel.rectb(24, y - 2, 208, 14, 7)
                self.draw_text(34, y, "▶ " + level["name"], 8, 10)
            else:
                self.draw_text(42, y, level["name"], 8, 7)

        self.draw_center_text(0, 150, 256, "↑↓でえらぶ / Enterでけってい", 8, 7)

        # ランキングボタン
        x = self.ranking_button["x"]
        y = self.ranking_button["y"]
        w = self.ranking_button["w"]
        h = self.ranking_button["h"]

        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        self.draw_center_text(x, y + 4, w, "ランキング", 8, 10)

    def draw_text(self, x, y, text, size=8, color=7):
        writer.draw(x, y, text, size, color)

    def draw_name_input(self):
        self.draw_center_text(0, 24, 256, "きろくこうしん！", 12, 8)
        self.draw_center_text(0, 52, 256, "なまえをいれてね", 8, 10)

        # 結果
        self.draw_center_text(
            0,
            76,
            256,
            f"じかん：{self.clear_time_sec}びょう / ミス：{self.miss_count}かい",
            8,
            7
        )

        # 名前入力欄
        pyxel.rect(58, 104, 140, 18, 1)
        pyxel.rectb(58, 104, 140, 18, 7)

        display_name = self.player_name

        # カーソル点滅
        if pyxel.frame_count % 30 < 15:
            display_name += "_"

        self.draw_center_text(58, 109, 140, display_name, 8, 10)

        self.draw_center_text(0, 144, 256, "A-Z / 0-9 でにゅうりょく", 8, 7)
        self.draw_center_text(0, 160, 256, "Enterでけってい", 8, 7)

    def draw_ranking(self):
        self.draw_center_text(0, 12, 256, "ランキング", 12, 10)

        # 表示対象のレベルと問題数
        if self.current_level is not None:
            level = self.current_level
            count = self.target_question_count
        else:
            level = self.levels[self.selected_level_index]
            count = self.question_count_options[self.selected_question_count_index]

        ranking_key = self.build_ranking_key(level["type"], count)
        records = self.get_records_for_key(ranking_key)

        self.draw_center_text(0, 34, 256, level["name"], 8, 7)
        self.draw_center_text(0, 48, 256, f"{count}もん", 8, 7)

        start_y = 68

        if len(records) == 0:
            self.draw_center_text(0, 96, 256, "まだきろくがありません", 8, 7)
        else:
            for i, record in enumerate(records[:self.max_ranking_count]):
                y = start_y + i * 18

                name = record.get("name", "NO NAME")
                time = record["clear_time_sec"]
                miss = record["miss_count"]

                text = f"{i + 1}. {name} {time}びょう ミス{miss}"

                color = 10 if i == 0 else 7
                self.draw_text(24, y, text, 8, color)

        self.draw_center_text(0, 170, 256, "Enter / Escでタイトルへ", 8, 7)

    def is_clicked(self, x, y, w, h):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y

            return x <= mx <= x + w and y <= my <= y + h

        return False

    def draw_center_text(self, x, y, w, text, size=8, color=7):
        text_width = len(text) * size
        draw_x = x + (w - text_width) // 2
        writer.draw(draw_x, y, text, size, color)
    
    def draw_count_select(self):
        self.draw_center_text(0, 24, 256, "もんだいすうをえらんでね", 8, 10)

        if self.current_level is not None:
            self.draw_center_text(0, 48, 256, self.current_level["name"], 8, 7)

        start_y = 76

        for i, count in enumerate(self.question_count_options):
            y = start_y + i * 20
            text = f"{i + 1}. {count}もん"

            if i == self.selected_question_count_index:
                pyxel.rect(70, y - 2, 116, 14, 1)
                pyxel.rectb(70, y - 2, 116, 14, 7)
                self.draw_text(84, y, "▶ " + text, 8, 10)
            else:
                self.draw_text(100, y, text, 8, 7)

        self.draw_center_text(0, 156, 256, "↑↓でえらぶ / Enterでけってい", 8, 7)
        self.draw_center_text(0, 170, 256, "Escでタイトルにもどる", 8, 7)
    
    def draw_clear(self):
        self.draw_center_text(0, 24, 256, "ステージクリア！", 12, 10)

        if self.current_level is not None:
            self.draw_center_text(0, 54, 256, self.current_level["name"], 8, 7)

        self.draw_center_text(
            0,
            78,
            256,
            f"{self.target_question_count}もん クリア",
            8,
            7
        )

        self.draw_center_text(
            0,
            96,
            256,
            f"じかん：{self.clear_time_sec}びょう",
            8,
            10
        )

        self.draw_center_text(
            0,
            114,
            256,
            f"ミス：{self.miss_count}かい",
            8,
            12
        )

        if self.is_new_best:
            self.draw_center_text(0, 136, 256, "きろくこうしん！", 8, 8)
        else:
            best = self.ranking_records.get(self.get_ranking_key())

            if best is not None:
                self.draw_center_text(
                    0,
                    136,
                    256,
                    f"ベスト：{best['clear_time_sec']}びょう / ミス{best['miss_count']}かい",
                    8,
                    7
                )

        self.draw_center_text(0, 164, 256, "Enterでタイトルへ", 8, 7)

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

            # 画像幅に合わせて名前を中央寄せ
            name_text_w = len(current_monster["name"]) * 8
            name_x = current_monster["draw_x"] + (
                current_monster["image_w"] - name_text_w
            ) // 2

            self.draw_text(
                name_x,
                current_monster["name_y"],
                current_monster["name"],
                8,
                7
            )

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
        self.draw_center_text(
            92,
            8,
            72,
            f"{self.correct_count}/{self.target_question_count}もん",
            8,
            7
        )

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

    def build_ranking_key(self, level_type, question_count):
        return f"{level_type}_{question_count}"


    def get_ranking_key(self):
        return self.build_ranking_key(
            self.current_level["type"],
            self.target_question_count
        )
    
    def get_records_for_key(self, ranking_key):
        records = self.ranking_records.get(ranking_key, [])

        # 以前の1件保存形式だった場合の保険
        if isinstance(records, dict):
            records = [records]

        return records
    
    def can_enter_ranking(self, new_record):
        ranking_key = self.get_ranking_key()
        records = self.get_records_for_key(ranking_key)

        # 5件未満なら必ず入る
        if len(records) < self.max_ranking_count:
            return True

        # 時間が短い順、同じならミスが少ない順
        records = sorted(
            records,
            key=lambda r: (r["clear_time_sec"], r["miss_count"])
        )

        worst_record = records[-1]

        new_score = (
            new_record["clear_time_sec"],
            new_record["miss_count"]
        )

        worst_score = (
            worst_record["clear_time_sec"],
            worst_record["miss_count"]
        )

        return new_score < worst_score
    
    def save_pending_record(self):
        if self.pending_record is None:
            return

        ranking_key = self.get_ranking_key()
        records = self.get_records_for_key(ranking_key)

        name = self.player_name.strip()
        if name == "":
            name = "NO NAME"

        new_record = self.pending_record.copy()
        new_record["name"] = name

        records.append(new_record)

        # 時間が短い順、同じならミスが少ない順
        records = sorted(
            records,
            key=lambda r: (r["clear_time_sec"], r["miss_count"])
        )

        # 上位5件だけ残す
        records = records[:self.max_ranking_count]

        self.ranking_records[ranking_key] = records
        self.save_ranking()

        self.pending_record = None
        self.player_name = ""


App()
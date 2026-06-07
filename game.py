import pyxel
import random
import json
import os


class App:
    def __init__(self):
        self.fps = 30
        pyxel.init(256, 192, title="Math Quest", fps=self.fps)
        self.font8 = pyxel.Font("misaki_gothic.ttf", 8)
        self.font10 = pyxel.Font("misaki_gothic.ttf", 10)
        self.font12 = pyxel.Font("misaki_gothic.ttf", 12)
        self.font14 = pyxel.Font("misaki_gothic.ttf", 14)
        self.font16 = pyxel.Font("misaki_gothic.ttf", 16)
        pyxel.mouse(True)  # PCテスト用

        # サウンド番号
        self.SOUND_OPENING_BGM = 0
        self.SOUND_BATTLE_BGM = 1
        self.SOUND_LAST_BATTLE_BGM = 2

        self.SOUND_SLIME_ATTACK = 3
        self.SOUND_GHOST_ATTACK = 4
        self.SOUND_GOREM_ATTACK = 5
        self.SOUND_DRAGON_ATTACK = 6
        self.SOUND_KING_ATTACK = 7

        self.SOUND_HERO_ATTACK = 8
        self.SOUND_CHEERS = 9

        # チャンネル番号
        self.BGM_CHANNEL = 0
        self.SE_CHANNEL = 1

        # 現在流れているBGM
        self.current_bgm = None

        # 音声ファイル読み込み
        pyxel.sounds[self.SOUND_OPENING_BGM].pcm("sounds/opening_music.ogg")
        pyxel.sounds[self.SOUND_BATTLE_BGM].pcm("sounds/battle_music.ogg")
        pyxel.sounds[self.SOUND_LAST_BATTLE_BGM].pcm("sounds/last_battle_music.ogg")

        pyxel.sounds[self.SOUND_SLIME_ATTACK].pcm("sounds/slime_sound.ogg")
        pyxel.sounds[self.SOUND_GHOST_ATTACK].pcm("sounds/ghost_sound.ogg")
        pyxel.sounds[self.SOUND_GOREM_ATTACK].pcm("sounds/gorem_sound.ogg")
        pyxel.sounds[self.SOUND_DRAGON_ATTACK].pcm("sounds/dragon_sound.ogg")
        pyxel.sounds[self.SOUND_KING_ATTACK].pcm("sounds/king_sound.ogg")

        pyxel.sounds[self.SOUND_HERO_ATTACK].pcm("sounds/slash_sound.ogg")
        pyxel.sounds[self.SOUND_CHEERS].pcm("sounds/cheers_sound.ogg")

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
        pyxel.images[2].load(184, 0, "king.png")      # 72×72

        # タイトル画面用アイコン
        self.title_icon_size = 24

        pyxel.images[0].load(48, 0, "shield.png")
        pyxel.images[0].load(80, 0, "sword.png")

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
            "draw_x": 38,
            "draw_y": 40,
            "name_y": 76,
            "max_hp": 5,
            "attack_sound": self.SOUND_SLIME_ATTACK,
        },
        {
            "name": "ゴースト",
            "image_bank": 2,
            "image_x": 0,
            "image_y": 0,
            "image_w": 38,
            "image_h": 38,
            "draw_x": 38,
            "draw_y": 38,
            "name_y": 76,
            "max_hp": 5,
            "attack_sound": self.SOUND_GHOST_ATTACK,
        },
        {
            "name": "ゴーレム",
            "image_bank": 2,
            "image_x": 48,
            "image_y": 0,
            "image_w": 46,
            "image_h": 46,
            "draw_x": 34,
            "draw_y": 30,
            "name_y": 76,
            "max_hp": 5,
            "attack_sound": self.SOUND_GOREM_ATTACK,
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
            "max_hp": 5,
            "attack_sound": self.SOUND_DRAGON_ATTACK,
        },
        {
            "name": "まおう",
            "image_bank": 2,
            "image_x": 184,
            "image_y": 0,
            "image_w": 72,
            "image_h": 72,
            "draw_x": 22,
            "draw_y": 12,
            "name_y": 82,
            "max_hp": 5,
            "attack_sound": self.SOUND_KING_ATTACK,
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

        # ランキング表示用
        self.selected_ranking_level_index = 0
        self.selected_ranking_count_index = 1

        self.ranking_view_level = None
        self.ranking_view_count = None

        # レベル情報
        self.levels = [
            {
                "name": "1けた たしざん・ひきざん",
                "type": "one_digit_add_sub",
                "monster_index": 0,
            },
            {
                "name": "2けた たしざん・ひきざん",
                "type": "two_digit_add_sub",
                "monster_index": 1,
            },
            {
                "name": "1けた かけざん",
                "type": "one_digit_multiply",
                "monster_index": 2,
            },
            {
                "name": "かんたん わりざん",
                "type": "simple_divide",
                "monster_index": 3,
            },
            {
                "name": "ぜんぶ",
                "type": "all_random",
                "monster_index": 4,
            },
        ]

        # 小文字変換
        self.small_char_map = {
            "あ": "ぁ",
            "い": "ぃ",
            "う": "ぅ",
            "え": "ぇ",
            "お": "ぉ",
            "や": "ゃ",
            "ゆ": "ゅ",
            "よ": "ょ",
            "つ": "っ",
            "わ": "ゎ",
        }

        # タイトル画面レイアウト
        self.title_level_x = 20
        self.title_level_y = 56
        self.title_level_w = 216
        self.title_level_h = 14
        self.title_level_gap = 5

        # ランキングボタン
        self.ranking_button = {
            "x": 134,
            "y": 166,
            "w": 100,
            "h": 16,
        }

        # 素材提供ボタン
        self.credit_button = {
            "x": 20,
            "y": 166,
            "w": 88,
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

        # 名前入力
        self.player_name = ""
        self.max_name_length = 10
        self.name_input_mode = "kana"  # kana / num

        # 連続タップ入力用
        self.active_kana_label = None
        self.active_kana_index = 0
        self.kana_cycle_timer = 0
        self.kana_cycle_limit = 30  # 30FPSなら約1秒

        # あかさたなキー
        self.kana_groups = [
            {"label": "あ", "chars": ["あ", "い", "う", "え", "お", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ"]},
            {"label": "か", "chars": ["か", "き", "く", "け", "こ"]},
            {"label": "さ", "chars": ["さ", "し", "す", "せ", "そ"]},
            {"label": "た", "chars": ["た", "ち", "つ", "て", "と", "っ"]},
            {"label": "な", "chars": ["な", "に", "ぬ", "ね", "の"]},
            {"label": "は", "chars": ["は", "ひ", "ふ", "へ", "ほ"]},
            {"label": "ま", "chars": ["ま", "み", "む", "め", "も"]},
            {"label": "や", "chars": ["や", "ゆ", "よ", "ゃ", "ゅ", "ょ"]},
            {"label": "ら", "chars": ["ら", "り", "る", "れ", "ろ"]},
            {"label": "わ", "chars": ["わ", "を", "ん", "ー", "ゎ"]},
        ]

        # 濁点・半濁点変換
        self.dakuten_map = {
            "か": "が", "き": "ぎ", "く": "ぐ", "け": "げ", "こ": "ご",
            "さ": "ざ", "し": "じ", "す": "ず", "せ": "ぜ", "そ": "ぞ",
            "た": "だ", "ち": "ぢ", "つ": "づ", "て": "で", "と": "ど",
            "は": "ば", "ひ": "び", "ふ": "ぶ", "へ": "べ", "ほ": "ぼ",
        }

        self.handakuten_map = {
            "は": "ぱ", "ひ": "ぴ", "ふ": "ぷ", "へ": "ぺ", "ほ": "ぽ",
        }

        pyxel.run(self.update, self.draw)

    def play_bgm(self, sound_id):
        if self.current_bgm == sound_id:
            return

        pyxel.stop(self.BGM_CHANNEL)
        pyxel.play(self.BGM_CHANNEL, sound_id, loop=True)
        self.current_bgm = sound_id


    def stop_bgm(self):
        pyxel.stop(self.BGM_CHANNEL)
        self.current_bgm = None
    
    def play_se(self, sound_id):
        pyxel.play(self.SE_CHANNEL, sound_id)
    
    def get_name_input_buttons(self):
        buttons = []

        button_w = 54
        button_h = 15
        cols = [28, 101, 174]
        start_y = 92
        row_gap = 17

        if self.name_input_mode == "kana":
            rows = [
                ["あ", "か", "さ"],
                ["た", "な", "は"],
                ["ま", "や", "ら"],
                ["わ", "゛", "゜"],
                ["すうじ", "けす", "OK"],
            ]

            for row_index, row in enumerate(rows):
                y = start_y + row_index * row_gap

                for col_index, label in enumerate(row):
                    x = cols[col_index]

                    if label == "すうじ":
                        button_type = "toggle_num"
                    elif label == "けす":
                        button_type = "delete"
                    elif label == "OK":
                        button_type = "ok"
                    elif label == "゛":
                        button_type = "dakuten"
                    elif label == "゜":
                        button_type = "handakuten"
                    else:
                        button_type = "kana_group"

                    buttons.append({
                        "label": label,
                        "type": button_type,
                        "x": x,
                        "y": y,
                        "w": button_w,
                        "h": button_h,
                    })

        elif self.name_input_mode == "num":
            rows = [
                ["1", "2", "3"],
                ["4", "5", "6"],
                ["7", "8", "9"],
                ["かな", "0", "けす"],
                ["", "", "OK"],
            ]

            for row_index, row in enumerate(rows):
                y = start_y + row_index * row_gap

                for col_index, label in enumerate(row):
                    if label == "":
                        continue

                    x = cols[col_index]

                    if label == "かな":
                        button_type = "toggle_kana"
                    elif label == "けす":
                        button_type = "delete"
                    elif label == "OK":
                        button_type = "ok"
                    else:
                        button_type = "num"

                    buttons.append({
                        "label": label,
                        "type": button_type,
                        "x": x,
                        "y": y,
                        "w": button_w,
                        "h": button_h,
                    })

        return buttons

    def make_question(self):
        level_type = self.current_level["type"]

        # 「ぜんぶ」ステージなら、そのたびに種類をランダム決定
        if level_type == "all_random":
            question_type = random.choice([
                "one_digit_add_sub",
                "two_digit_add_sub",
                "one_digit_multiply",
                "simple_divide",
            ])
        else:
            question_type = level_type

        if question_type == "one_digit_add_sub":
            self.make_one_digit_add_sub_question()

        elif question_type == "two_digit_add_sub":
            self.make_two_digit_add_sub_question()

        elif question_type == "one_digit_multiply":
            self.make_one_digit_multiply_question()

        elif question_type == "simple_divide":
            self.make_simple_divide_question()

        self.input_text = ""
        self.time_left = self.time_limit
    
    def make_one_digit_add_sub_question(self):
        op = random.choice(["+", "-"])

        self.a = random.randint(1, 9)
        self.b = random.randint(1, 9)

        if op == "+":
            self.answer = self.a + self.b
        else:
            if self.a < self.b:
                self.a, self.b = self.b, self.a
            self.answer = self.a - self.b

        self.op = op


    def make_two_digit_add_sub_question(self):
        op = random.choice(["+", "-"])

        self.a = random.randint(10, 99)
        self.b = random.randint(10, 99)

        if op == "+":
            self.answer = self.a + self.b
        else:
            if self.a < self.b:
                self.a, self.b = self.b, self.a
            self.answer = self.a - self.b

        self.op = op


    def make_one_digit_multiply_question(self):
        self.a = random.randint(1, 9)
        self.b = random.randint(1, 9)
        self.answer = self.a * self.b
        self.op = "x"


    def make_simple_divide_question(self):
        # 割り切れる問題だけ作る
        self.b = random.randint(1, 9)
        self.answer = random.randint(1, 9)
        self.a = self.b * self.answer
        self.op = "÷"

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
        self.stop_bgm()
        self.play_se(self.SOUND_CHEERS)
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
                self.return_to_title_after_game_over()

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
        elif self.scene == "ranking_level_select":
            self.update_ranking_level_select()
        elif self.scene == "ranking_count_select":
            self.update_ranking_count_select()
        elif self.scene == "credit":
            self.update_credit()
    
    def update_title(self):
        # タイトルBGM
        self.play_bgm(self.SOUND_OPENING_BGM)

        # レベルボタンをクリック
        for i, level in enumerate(self.levels):
            y = self.title_level_y + i * (self.title_level_h + self.title_level_gap)

            if self.is_clicked(self.title_level_x, y, self.title_level_w, self.title_level_h):
                self.select_level(i)
                return

        # ランキングボタンをクリック
        if self.is_clicked(
            self.ranking_button["x"],
            self.ranking_button["y"],
            self.ranking_button["w"],
            self.ranking_button["h"]
        ):
            self.scene = "ranking_level_select"
            return

        # 素材提供ボタンをクリック
        if self.is_clicked(
            self.credit_button["x"],
            self.credit_button["y"],
            self.credit_button["w"],
            self.credit_button["h"]
        ):
            self.scene = "credit"
            return
    
    def update_ranking_level_select(self):
        button_x = 20
        button_y = 48
        button_w = 216
        button_h = 16
        button_gap = 7

        for i, level in enumerate(self.levels):
            y = button_y + i * (button_h + button_gap)

            if self.is_clicked(button_x, y, button_w, button_h):
                self.selected_ranking_level_index = i
                self.scene = "ranking_count_select"
                return

        # タイトルにもどる
        if self.is_clicked(58, 164, 140, 18):
            self.scene = "title"
            return
    
    def update_count_select(self):
        button_x = 78
        button_w = 100
        button_h = 18
        start_y = 72

        for i, count in enumerate(self.question_count_options):
            y = start_y + i * 26

            if self.is_clicked(button_x, y, button_w, button_h):
                self.selected_question_count_index = i
                self.start_level()
                return

        # タイトルにもどる
        if self.is_clicked(58, 158, 140, 18):
            self.scene = "title"
            return

    def update_name_input(self):
        # 連続タップの受付時間を減らす
        if self.kana_cycle_timer > 0:
            self.kana_cycle_timer -= 1

            if self.kana_cycle_timer <= 0:
                self.reset_kana_cycle()

        for button in self.get_name_input_buttons():
            if self.is_clicked(button["x"], button["y"], button["w"], button["h"]):
                button_type = button["type"]

                if button_type == "kana_group":
                    for group in self.kana_groups:
                        if group["label"] == button["label"]:
                            self.input_kana_group(group)
                            break

                elif button_type == "num":
                    if len(self.player_name) < self.max_name_length:
                        self.player_name += button["label"]
                    self.reset_kana_cycle()

                elif button_type == "delete":
                    self.player_name = self.player_name[:-1]
                    self.reset_kana_cycle()

                elif button_type == "dakuten":
                    self.apply_mark_to_last_char("dakuten")

                elif button_type == "handakuten":
                    self.apply_mark_to_last_char("handakuten")

                elif button_type == "toggle_num":
                    self.name_input_mode = "num"
                    self.reset_kana_cycle()

                elif button_type == "toggle_kana":
                    self.name_input_mode = "kana"
                    self.reset_kana_cycle()

                elif button_type == "ok":
                    self.save_pending_record()
                    self.reset_kana_cycle()
                    self.scene = "ranking"

                return
    
    def update_credit(self):
        # タイトルBGMをそのまま流す
        self.play_bgm(self.SOUND_OPENING_BGM)

        # タイトルにもどるボタン
        if self.is_clicked(58, 158, 140, 18):
            self.scene = "title"
            return
    
    def draw_credit(self):
        self.draw_center_text(0, 20, 256, "ていきょう", 16, 10)

        # BGM
        pyxel.rect(28, 58, 200, 30, 1)
        pyxel.rectb(28, 58, 200, 30, 7)
        self.draw_text(48, 70, "BGM", 8, 7)
        self.draw_text(112, 66, "魔王魂", 16, 10)

        # 効果音
        pyxel.rect(28, 102, 200, 30, 1)
        pyxel.rectb(28, 102, 200, 30, 7)
        self.draw_text(40, 114, "こうかおん", 8, 7)
        self.draw_text(100, 110, "効果音ラボ", 16, 10)

        # 戻るボタン
        pyxel.rect(58, 158, 140, 18, 1)
        pyxel.rectb(58, 158, 140, 18, 7)
        self.draw_center_text(58, 163, 140, "タイトルにもどる", 8, 7)

    def update_ranking(self):
        if self.is_clicked(58, 164, 140, 18):
            self.message = ""
            self.input_text = ""
            self.scene = "title"
            return

    def select_level(self, level_index):
        self.selected_level_index = level_index
        self.current_level = self.levels[level_index]

        # 問題数選択は毎回10問から開始
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

        self.ranking_view_level = None
        self.ranking_view_count = None

        self.monster_defeated = False
        self.player_defeated = False
        self.attack_animating = False
        self.monster_attack_animating = False
        self.time_up_waiting = False

        self.make_question()

        current_monster = self.monsters[self.current_monster_index]

        if current_monster["name"] == "まおう":
            self.play_bgm(self.SOUND_LAST_BATTLE_BGM)
        else:
            self.play_bgm(self.SOUND_BATTLE_BGM)

        self.scene = "battle"

    def return_to_title_after_game_over(self):
        self.player_defeated = False
        self.monster_defeated = False
        self.attack_animating = False
        self.monster_attack_animating = False
        self.time_up_waiting = False

        self.message = ""
        self.input_text = ""

        self.player_hp = self.player_max_hp

        # 今選んでいたモンスターのHPを戻す
        if self.current_level is not None:
            self.current_monster_index = self.current_level["monster_index"]

        self.monster_max_hp = self.target_question_count
        self.monster_hp = self.monster_max_hp

        self.scene = "title"

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

        # 勇者の攻撃音
        self.play_se(self.SOUND_HERO_ATTACK)
    
    def start_monster_attack(self):
        self.monster_attack_animating = True
        self.monster_attack_timer = self.monster_attack_total_frames
        self.monster_attack_hit_done = False

        self.monster_attack_dx = 0
        self.hero_shake_x = 0
        self.pending_player_defeat = False

        self.message = "まちがい！"
        self.message_color = 12

        # 現在のモンスターの攻撃音
        current_monster = self.monsters[self.current_monster_index]
        self.play_se(current_monster["attack_sound"])


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
        elif self.scene == "ranking_level_select":
            self.draw_ranking_level_select()
        elif self.scene == "ranking_count_select":
            self.draw_ranking_count_select()
        elif self.scene == "credit":
            self.draw_credit()

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
        # 左上：盾
        pyxel.blt(18, 16, 0, 48, 0, self.title_icon_size, self.title_icon_size, 0)

        # 右上：剣
        pyxel.blt(214, 16, 0, 80, 0, self.title_icon_size, self.title_icon_size, 0)

        # タイトル
        self.draw_center_text(0, 18, 256, "けいさん　クエスト", 16, 7)

        # サブタイトル
        self.draw_center_text(0, 40, 256, "レベルをえらんでね", 8, 10)

        # レベルボタン
        for i, level in enumerate(self.levels):
            y = self.title_level_y + i * (self.title_level_h + self.title_level_gap)

            pyxel.rect(self.title_level_x, y, self.title_level_w, self.title_level_h, 1)
            pyxel.rectb(self.title_level_x, y, self.title_level_w, self.title_level_h, 7)

            color = 10 if i == self.selected_level_index else 7
            self.draw_center_text(
                self.title_level_x,
                y + 3,
                self.title_level_w,
                level["name"],
                8,
                color
            )

        # 素材提供ボタン
        cx = self.credit_button["x"]
        cy = self.credit_button["y"]
        cw = self.credit_button["w"]
        ch = self.credit_button["h"]

        pyxel.rect(cx, cy, cw, ch, 1)
        pyxel.rectb(cx, cy, cw, ch, 7)
        self.draw_center_text(cx, cy + 4, cw, "ていきょう", 8, 7)

        # ランキングボタン
        rx = self.ranking_button["x"]
        ry = self.ranking_button["y"]
        rw = self.ranking_button["w"]
        rh = self.ranking_button["h"]

        pyxel.rect(rx, ry, rw, rh, 1)
        pyxel.rectb(rx, ry, rw, rh, 7)
        self.draw_center_text(rx, ry + 4, rw, "ランキング", 8, 10)
    
    def draw_ranking_level_select(self):
        self.draw_center_text(0, 18, 256, "ランキング", 12, 10)
        self.draw_center_text(0, 38, 256, "レベルをえらんでね", 8, 7)

        button_x = 20
        button_y = 48
        button_w = 216
        button_h = 16
        button_gap = 7

        for i, level in enumerate(self.levels):
            y = button_y + i * (button_h + button_gap)

            pyxel.rect(button_x, y, button_w, button_h, 1)
            pyxel.rectb(button_x, y, button_w, button_h, 7)

            color = 10 if i == self.selected_ranking_level_index else 7
            self.draw_center_text(button_x, y + 4, button_w, level["name"], 8, color)

        # タイトルにもどるボタン
        pyxel.rect(58, 164, 140, 18, 1)
        pyxel.rectb(58, 164, 140, 18, 7)
        self.draw_center_text(58, 169, 140, "タイトルにもどる", 8, 7)
    
    def update_ranking_count_select(self):
        button_x = 78
        button_w = 100
        button_h = 18
        start_y = 72

        for i, count in enumerate(self.question_count_options):
            y = start_y + i * 26

            if self.is_clicked(button_x, y, button_w, button_h):
                self.selected_ranking_count_index = i

                self.ranking_view_level = self.levels[self.selected_ranking_level_index]
                self.ranking_view_count = count

                self.scene = "ranking"
                return

        # レベル選択にもどる
        if self.is_clicked(58, 158, 140, 18):
            self.scene = "ranking_level_select"
            return
    
    def draw_ranking_count_select(self):
        self.draw_center_text(0, 20, 256, "ランキング", 12, 10)

        level = self.levels[self.selected_ranking_level_index]

        self.draw_center_text(0, 46, 256, level["name"], 8, 7)
        self.draw_center_text(0, 62, 256, "もんだいすうをえらんでね", 8, 10)

        button_x = 78
        button_w = 100
        button_h = 18
        start_y = 88

        for i, count in enumerate(self.question_count_options):
            y = start_y + i * 24

            pyxel.rect(button_x, y, button_w, button_h, 1)
            pyxel.rectb(button_x, y, button_w, button_h, 7)

            color = 10 if i == self.selected_ranking_count_index else 7
            self.draw_center_text(button_x, y + 5, button_w, f"{count}もん", 8, color)

        # レベル選択にもどるボタン
        pyxel.rect(58, 158, 140, 18, 1)
        pyxel.rectb(58, 158, 140, 18, 7)
        self.draw_center_text(58, 163, 140, "レベルにもどる", 8, 7)

    def get_font(self, size):
        if size == 10:
            return self.font10
        elif size == 12:
            return self.font12
        elif size == 14:
            return self.font14
        elif size == 16:
            return self.font16
        else:
            return self.font8


    def draw_text(self, x, y, text, size=8, color=7):
        pyxel.text(x, y, text, color, self.get_font(size))

    def is_clicked(self, x, y, w, h):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            return x <= mx <= x + w and y <= my <= y + h

        return False

    def draw_name_input(self):
        self.draw_center_text(0, 12, 256, "きろくこうしん！", 15, 8)
        self.draw_center_text(0, 36, 256, "なまえをいれてね", 8, 10)

        self.draw_center_text(
            0,
            54,
            256,
            f"じかん：{self.clear_time_sec}びょう / ミス：{self.miss_count}かい",
            8,
            7
        )

        # 名前入力欄
        pyxel.rect(58, 70, 140, 16, 1)
        pyxel.rectb(58, 70, 140, 16, 7)

        display_name = self.player_name
        if pyxel.frame_count % 30 < 15:
            display_name += "_"

        self.draw_center_text(58, 74, 140, display_name, 8, 10)

        # 入力モード
        mode_text = "かな" if self.name_input_mode == "kana" else "すうじ"
        self.draw_text(18, 184, f"モード:{mode_text}", 8, 7)

        # ボタン描画
        for button in self.get_name_input_buttons():
            x = button["x"]
            y = button["y"]
            w = button["w"]
            h = button["h"]

            pyxel.rect(x, y, w, h, 5)
            pyxel.rectb(x, y, w, h, 7)

            self.draw_center_text(
                x,
                y + 4,
                w,
                button["label"],
                8,
                7
            )

    def draw_ranking(self):
        self.draw_center_text(0, 12, 256, "ランキング", 12, 10)

        # 表示対象のレベルと問題数
        if self.ranking_view_level is not None:
            level = self.ranking_view_level
            count = self.ranking_view_count
        elif self.current_level is not None:
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

                name = record.get("name", "なまえ　なし")
                time = record["clear_time_sec"]
                miss = record["miss_count"]

                text = f"{i + 1}. {name}　：　{time}びょう ミス{miss}"

                color = 10 if i == 0 else 7
                self.draw_text(24, y, text, 8, color)

        self.draw_center_text(0, 170, 256, "タイトルにもどる", 8, 7)

    def is_clicked(self, x, y, w, h):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y

            return x <= mx <= x + w and y <= my <= y + h

        return False

    def draw_center_text(self, x, y, w, text, size=8, color=7):
        font = self.get_font(size)
        text_width = font.text_width(text)
        draw_x = x + (w - text_width) // 2
        pyxel.text(draw_x, y, text, color, font)
    
    def draw_count_select(self):
        self.draw_center_text(0, 22, 256, "もんだいすうをえらんでね", 8, 10)

        if self.current_level is not None:
            self.draw_center_text(0, 46, 256, self.current_level["name"], 8, 7)

        button_x = 78
        button_w = 100
        button_h = 18
        start_y = 72

        for i, count in enumerate(self.question_count_options):
            y = start_y + i * 26

            pyxel.rect(button_x, y, button_w, button_h, 1)
            pyxel.rectb(button_x, y, button_w, button_h, 7)

            color = 10 if i == self.selected_question_count_index else 7
            self.draw_center_text(button_x, y + 5, button_w, f"{count}もん", 8, color)

        # タイトルにもどるボタン
        pyxel.rect(58, 158, 140, 18, 1)
        pyxel.rectb(58, 158, 140, 18, 7)
        self.draw_center_text(58, 163, 140, "タイトルにもどる", 8, 7)
    
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
            name = "なまえ　なし"

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
    
    def apply_mark_to_last_char(self, mark_type):
        if self.player_name == "":
            return

        last_char = self.player_name[-1]
        before_text = self.player_name[:-1]

        if mark_type == "dakuten":
            converted_char = self.dakuten_map.get(last_char)
        elif mark_type == "handakuten":
            converted_char = self.handakuten_map.get(last_char)
        else:
            converted_char = None

        if converted_char is not None:
            self.player_name = before_text + converted_char
            self.reset_kana_cycle()
    
    def apply_small_to_last_char(self):
        if self.player_name == "":
            return

        last_char = self.player_name[-1]
        before_text = self.player_name[:-1]

        converted_char = self.small_char_map.get(last_char)

        if converted_char is not None:
            self.player_name = before_text + converted_char
            self.reset_kana_cycle()

    def reset_kana_cycle(self):
        self.active_kana_label = None
        self.active_kana_index = 0
        self.kana_cycle_timer = 0

    def input_kana_group(self, group):
        chars = group["chars"]

        # 同じキーを制限時間内に押したら、最後の文字を切り替える
        if (
            self.active_kana_label == group["label"]
            and self.kana_cycle_timer > 0
            and self.player_name != ""
        ):
            self.active_kana_index += 1

            if self.active_kana_index >= len(chars):
                self.active_kana_index = 0

            self.player_name = self.player_name[:-1] + chars[self.active_kana_index]

        # 違うキー、または時間が空いたら、新しい文字として追加
        else:
            if len(self.player_name) >= self.max_name_length:
                return

            self.active_kana_label = group["label"]
            self.active_kana_index = 0
            self.player_name += chars[0]

        self.kana_cycle_timer = self.kana_cycle_limit


App()
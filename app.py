import streamlit as st
import random
import pandas as pd
import os
# ページ設定
st.set_page_config(page_title="Streamlit Roguelike", layout="wide")

# --- 1. データ定義 ---
CHARACTER_POOL = {
    "ブロッカー": [
        {"name": "聖騎士アルタニア", "hp": 150, "atk": 10, "df": 20, "role": "ブロッカー","skill": "鉄壁の構え", "skill_duration": 0, "image": "assets/altania.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "鉄壁のゴライアス", "hp": 180, "atk": 8, "df": 25, "role": "ブロッカー","skill": "物理反射", "skill_duration": 0, "image": "assets/golaias.png", "weapon_slots": [None, None], "armor_slot": None}
    ],
    "アタッカー": [
        {"name": "魔術師エルザ", "hp": 80, "atk": 25, "df": 5, "role": "アタッカー","skill": "連携攻撃", "skill_duration": 0, "image": "assets/elsa.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "暗殺者レイジ", "hp": 90, "atk": 22, "df": 8, "role": "アタッカー","skill": "毒攻撃", "skill_duration": 0, "image": "assets/reizi.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "狩人シルフ", "hp": 95, "atk": 20, "df": 10, "role": "アタッカー","skill": "遠距離攻撃", "skill_duration": 0, "image": "assets/silf.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "狂戦士バルド", "hp": 120, "atk": 18, "df": 12, "role": "アタッカー","skill": "吸収", "skill_duration": 0, "image": "assets/vald.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "侍ムサシ", "hp": 100, "atk": 24, "df": 9, "role": "アタッカー", "skill": "機動攻撃", "skill_duration": 0,"image": "assets/musasi.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "竜騎士ジーク", "hp": 110, "atk": 21, "df": 14, "role": "アタッカー","skill": "貫通攻撃", "skill_duration": 0, "image": "assets/jeek.png", "weapon_slots": [None, None], "armor_slot": None}
    ],
    "ヒーラー": [
        {"name": "司祭セシリア", "hp": 85, "atk": 8, "df": 7, "role": "ヒーラー", "heal": 20,"skill": "リジェネレーション", "skill_duration": 0, "image": "assets/sesiria.png", "weapon_slots": [None, None], "armor_slot": None},
        {"name": "吟遊詩人アリア", "hp": 90, "atk": 10, "df": 10, "role": "ヒーラー", "heal": 15,"skill": "聖なる陣形", "skill_duration": 0, "image": "assets/alia.png", "weapon_slots": [None, None], "armor_slot": None}
    ]
}
# エリアごとの敵プール (通常モブとボスをエリア別に定義)
ENEMY_POOL = {
    1: {
        "normal": [
            {"name": "ゴブリン", "hp": 45, "atk": 12, "df": 5, "image": "assets/goblin.png"},
            {"name": "大コウモリ", "hp": 30, "atk": 15, "df": 2, "image": "assets/bat.png"},
            {"name": "マンドレイク", "hp": 40, "atk": 10, "df": 4, "image": "assets/mandrake.png"},
            {"name": "フォレストウルフ", "hp": 55, "atk": 16, "df": 6, "image": "assets/wolf.png"},
            {"name": "グリーンスライム", "hp": 60, "atk": 8, "df": 12, "image": "assets/slime.png"}
        ],
        "boss": {"name": "ゴブリンキング", "hp": 300, "atk": 25, "df": 12, "image": "assets/goblin_king.png"}
    },
    2: {
        "normal": [
            {"name": "オーク", "hp": 70, "atk": 18, "df": 8, "image": "assets/orc.png"},
            {"name": "スケルトンソルジャー", "hp": 60, "atk": 20, "df": 5, "image": "assets/skeleton.png"},
            {"name": "迷い子のゴースト", "hp": 50, "atk": 15, "df": 3, "image": "assets/ghost.png"},
            {"name": "巨大毒サソリ", "hp": 65, "atk": 16, "df": 7, "image": "assets/scorpion.png"},
            {"name": "マインミミック", "hp": 80, "atk": 12, "df": 15, "image": "assets/mimic.png"}
        ],
        "boss": {"name": "影の支配者リッチ", "hp": 500, "atk": 32, "df": 18, "image": "assets/lich_boss.png"}
    }, # エリア2〜5も同様にパラメータと画像パスを設定
    3: {
        "normal": [
            {"name": "マグモスライム", "hp": 100, "atk": 15, "df": 12, "image": "assets/magma_slime.png"},
            {"name": "ファイアバード", "hp": 80, "atk": 25, "df": 6, "image": "assets/fire_bird.png"},
            {"name": "サラマンダー", "hp": 90, "atk": 22, "df": 8, "image": "assets/salamander.png"},
            {"name": "ストーンゴーレム", "hp": 120, "atk": 20, "df": 20, "image": "assets/golem.png"},
            {"name": "ラヴァインプ", "hp": 70, "atk": 18, "df": 5, "image": "assets/lava_imp.png"}
        ],
        "boss": {"name": "古代の重戦車", "hp": 700, "atk": 40, "df": 30, "image": "assets/stone_boss.png"}
    }, 
    4: {
        "normal": [
            {"name": "マーダーラプトル", "hp": 110, "atk": 30, "df": 10, "image": "assets/raptor.png"},
            {"name": "アポカリプスウィスプ", "hp": 90, "atk": 35, "df": 5, "image": "assets/wisp.png"},
            {"name": "ガーゴイル", "hp": 100, "atk": 28, "df": 12, "image": "assets/gargoyle.png"},
            {"name": "テンタクルウォーター", "hp": 130, "atk": 22, "df": 15, "image": "assets/tentacle.png"},
            {"name": "ミストシーフ", "hp": 95, "atk": 32, "df": 8, "image": "assets/thief.png"}
        ],
        "boss": {"name": "瀑布の妖姫セイレーン", "hp": 900, "atk": 50, "df": 22, "image": "assets/siren_boss.png"}
    }, 
    5: {
        "normal": [
            {"name": "ドラゴニュート", "hp": 150, "atk": 40, "df": 18, "image": "assets/dragoniut.png"},
            {"name": "キマイラ", "hp": 140, "atk": 38, "df": 15, "image": "assets/chimera.png"},
            {"name": "アークデーモン", "hp": 120, "atk": 45, "df": 10, "image": "assets/demon.png"},
            {"name": "アーマードナイト", "hp": 180, "atk": 30, "df": 25, "image": "assets/armored_knight.png"},
            {"name": "イビルアイ", "hp": 110, "atk": 35, "df": 12, "image": "assets/evil_eye.png"}
        ],
        "boss": {"name": "終焉の紅蓮竜", "hp": 1200, "atk": 65, "df": 35, "image": "assets/dragon_boss.png"}
    }
}
EVENT_TYPES = ["戦闘", "装備獲得", "アイテム獲得", "回復", "スキル獲得"]
def display_character_card(cell, is_ally):
    # 画像が存在すれば表示、なければダミーの箱を表示
    if os.path.exists(cell["image"]):
        st.image(cell["image"], use_container_width=True)
    else:
        placeholder_color = "🔵" if is_ally else "🔴"
        st.markdown(f"<div style='text-align:center;font-size:40px;background:#eee;padding:10px;border-radius:5px;'>{placeholder_color}</div>", unsafe_allow_html=True)
    if cell.get("skill_duration", 0) > 0:
        st.markdown(f"**⚡ {cell['skill']} (残り {cell['skill_duration']}T)**")
    # キャラクター名とHPバーの表示
    st.caption(f"**{cell['name']}**")
    st.progress(max(0.0, min(1.0, cell["hp"] / cell["max_hp"])))
    
    if is_ally:
        st.markdown(f"<small>HP: {max(0, cell['hp'])}/{cell['max_hp']}</small>", unsafe_allow_html=True)
    else:
        if cell["hp"] > 0:
            st.markdown(f"<small style='color:red;'>HP: {cell['hp']}/{cell['max_hp']}</small>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center;color:gray;padding-top:20px;'>💀 撃破</div>", unsafe_allow_html=True)
# --- 2. 状態の初期化 ---
if "phase" not in st.session_state:
    st.session_state.phase = "CHARACTER_SELECT"  # CHARACTER_SELECT, EXPLORE, BATTLE, GAME_OVER, CLEAR
    st.session_state.party = []
    st.session_state.grid_ally = {f"{r},{c}": None for r in range(3) for c in range(3)}
    st.session_state.grid_enemy = {f"{r},{c}": None for r in range(3) for c in range(3)}
    st.session_state.area = 1
    st.session_state.event_count = 0
    st.session_state.current_choices = []
    st.session_state.battle_log = []
    st.session_state.current_enemy_boss = False
    if "exp" not in st.session_state: st.session_state.exp = 0
    if "level" not in st.session_state: st.session_state.level = 1
    if "gold" not in st.session_state: st.session_state.gold = 0
    if "shop_items" not in st.session_state:
        st.session_state.shop_items = [
            {"name": "鋼鉄の剣", "type": "weapon", "atk": 5, "price": 100},
            {"name": "皮の盾", "type": "armor", "df": 3, "price": 80},
        ]    
# --- 3. 関数定義 ---
def get_total_stats(char):
    """キャラクターの基礎ステータス＋装備補正を返す"""
    atk_bonus = 0
    df_bonus = 0
    
    # 武器スロットの加算
    for weapon in char.get("weapon_slots", []):
        if weapon:
            atk_bonus += weapon.get("atk", 0)
            
    # 防具スロットの加算
    armor = char.get("armor_slot")
    if armor:
        df_bonus += armor.get("df", 0)
        
    return {
        "atk": char["atk"] + atk_bonus,
        "df": char["df"] + df_bonus
    }
def generate_choices():
    return random.sample(EVENT_TYPES, 3)

def init_enemy(is_boss=False):
    """
    敵の初期配置を行う関数。
    ボス戦の場合は、ボス専用のデータをロードし、召喚可能なノーマル敵リストも保持する。
    """
    st.session_state.grid_enemy = {f"{r},{c}": None for r in range(3) for c in range(3)}
    area_pool = ENEMY_POOL[st.session_state.area]
    
    if is_boss:
        # ボスデータのコピーを作成
        boss_data = area_pool["boss"].copy()
        boss_data["max_hp"] = boss_data["hp"]
        # ボスは中央前衛 (1, 1) に配置
        st.session_state.grid_enemy["1,1"] = boss_data
        # 召喚用にノーマル敵のデータを保持しておく
        st.session_state.summonable_enemies = area_pool["normal"]
    else:
        # 通常モンスターをランダムに1〜3体配置
        num_enemies = random.randint(1, 3)
        available_slots = [f"{r},{c}" for r in range(3) for c in range(3)]
        chosen_slots = random.sample(available_slots, num_enemies)
        
        for slot in chosen_slots:
            enemy_template = random.choice(area_pool["normal"])
            enemy_data = enemy_template.copy()
            enemy_data["max_hp"] = enemy_data["hp"]
            st.session_state.grid_enemy[slot] = enemy_data
def apply_skill_logic(char, log):
    # 1. ターン経過による持続効果の減少
    if char.get("skill_duration", 0) > 0:
        char["skill_duration"] -= 1
        if char["skill_duration"] == 0:
            log.append(f"ℹ️ {char['name']} のスキル効果が切れた。")

    # 2. スキル発動判定（確率30%で発動）
    if char.get("skill_duration", 0) == 0 and random.random() < 0.3:
        char["skill_duration"] = 2  # 2ターン持続
        log.append(f"✨ {char['name']} がスキル『{char['skill']}』を発動！")
        return True # スキル発動時は通常攻撃をスキップ
    return False
def get_column_allies(col_idx):
    """指定された列(0,1,2)の味方リストを返す"""
    return [c for pos, c in st.session_state.grid_ally.items() if c and pos.endswith(f",{col_idx}")]

def get_row_enemies(row_idx):
    """指定された行(0,1,2)の敵リストを返す"""
    return [e for pos, e in st.session_state.grid_enemy.items() if e and pos.startswith(f"{row_idx},")]    
def run_battle_turn():
    # 簡易自動戦闘シミュレーションロジック
    log = []
    last_attacked_enemy = None
    # 1. ヒーラーの行動判定（攻撃前に回復を行う）
    for pos, char in st.session_state.grid_ally.items():
        if char and char["role"] == "ヒーラー" and char["hp"] > 0:
            # --- スキル発動処理 ---
            # 確率(30%)でスキル発動、かつ未発動状態ならスキル実行
            if char.get("skill_duration", 0) == 0 and random.random() < 0.3:
                char["skill_duration"] = 3 # 3ターン持続
                log.append(f"✨ {char['name']} がスキル『{char['skill']}』を発動！")
                
                # 各スキルの固有効果を実行
                if char["skill"] == "リジェネレーション":
                    # ターゲットの味方に継続回復付与（ここでは一時的に全味方に付与する等の処理が可能）
                    for ally in st.session_state.grid_ally.values():
                        if ally and ally["hp"] > 0:
                            ally["is_regen"] = True # リジェネフラグを立てる
                elif char["skill"] == "聖なる陣形（配置バフ）":
                    # 陣形バフ：同じ列の味方の防御を一時強化
                    col_idx = pos.split(",")[1]
                    for ally in get_column_allies(col_idx):
                        ally["df"] += 5
                        ally["df_buff_duration"] = 3
                
                char["did_act"] = True # 行動済みフラグ
    
            # --- 通常回復処理（スキル発動しなかった場合） ---
            else:
                # 味方全員のHP割合をチェック
                allies = [c for c in st.session_state.grid_ally.values() if c and c["hp"] > 0]
                if not allies: continue
                
                # HP割合が最小のキャラを探す
                lowest_hp_ally = min(allies, key=lambda x: x["hp"] / x["max_hp"])
                
                # 全員がHP最大か判定
                all_full = all(c["hp"] == c["max_hp"] for c in allies)
                
                    
                if not all_full:
                    # 回復処理
                    heal_amount = char.get("heal", 20)
                    lowest_hp_ally["hp"] = min(lowest_hp_ally["max_hp"], lowest_hp_ally["hp"] + heal_amount)
                    log.append(f"✨ {char['name']} が {lowest_hp_ally['name']} を回復した！")
                    # ヒーラー自身は回復後に攻撃しない仕様とするため、フラグなどで制御が必要だが、
                    # ここでは簡易的に「回復した場合は攻撃処理をスキップ」させる仕組みにする
                    char["did_act"] = True 
                else:
                    char["did_act"] = False # 攻撃処理へ回す
    
    for char in st.session_state.grid_ally.values():
        if char and char.get("is_regen"):
            char["hp"] = min(char["max_hp"], char["hp"] + 10)
            log.append(f"🌿 {char['name']} のリジェネでHPが回復した！")
    # 味方の攻撃
    for pos, char in st.session_state.grid_ally.items():
        if not char or char["hp"] <= 0 or char.get("did_act", False):
            continue
            
        # スキル発動判定（攻撃系）
        if apply_skill_logic(char, log):
            continue
        # 生きている敵を探す
        alive_enemies = [k for k, v in st.session_state.grid_enemy.items() if v and v["hp"] > 0]
        if alive_enemies:
            target_pos = random.choice(alive_enemies)
            enemy = st.session_state.grid_enemy[target_pos]
            last_attacked_enemy=enemy
            stats = get_total_stats(char)
            damage = max(1, stats["atk"] - enemy["df"])
            enemy["hp"] -= damage
            log.append(f"⚔️ {char['name']} が {enemy['name']} に {damage} ダメージ！")
            # 例：暗殺者レイジの「毒攻撃」
            if char.get("skill") == "毒攻撃" and char.get("skill_duration", 0) > 0:
                enemy["hp"] -= 5 # 追加の継続ダメージ
                log.append(f"🧪 毒による追加ダメージ！")
            # --- スキル処理分岐 ---
            # 1. 侍ムサシ：バックスタブ
            elif char["skill"] == "バックスタブ" and random.random() < 0.3:
                # 敵の最後列を特定して攻撃
                targets = [v for k, v in st.session_state.grid_enemy.items() if k.endswith(",0") and v]
                if targets:
                    target = random.choice(targets)
                    target["hp"] -= (damage * 1.5)
                    # 位置入れ替え（簡易版：自分を最前列へ）
                    st.session_state.grid_ally[pos] = None
                    st.session_state.grid_ally[pos.replace(",0", ",2")] = char
                    log.append(f"🗡️ ムサシのバックスタブ！位置を入れ替えた！")
            
            # 2. 狩人シルフ：ピアッシング・ショット
            elif char["skill"] == "ピアッシング・ショット" and random.random() < 0.3:
                for e in st.session_state.grid_enemy.values():
                    if e and e["hp"] > 0: e["hp"] -= damage * 0.5
                log.append(f"🏹 シルフの全体攻撃！")
    
            # 3. 竜騎士ジーク：貫通攻撃（同列の敵）
            elif char["skill"] == "貫通攻撃" and random.random() < 0.3:
                row_idx = pos.split(",")[0]
                for e in get_row_enemies(row_idx):
                    e["hp"] -= damage
                log.append(f"🐉 ジークの貫通攻撃！")
    
            # 4. 魔術師エルザ：連携攻撃
            elif char["skill"] == "連携攻撃（シナジー）" and last_attacked_enemy:
                last_attacked_enemy["hp"] -= damage * 0.8
                log.append(f"✨ エルザの追撃！")
    
            # 5. 狂戦士バルド：吸収
            elif char["skill"] == "吸収" and random.random() < 0.3:
                last_attacked_enemy["hp"] -= damage
                char["hp"] += char["atk"]
            
        if enemy["hp"] <= 0:
            log.append(f"💥 {enemy['name']} を倒した！")
        # 次のターンのためにフラグをリセット
        if char["role"] == "ヒーラー":
            char["did_act"] = False
    if st.session_state.current_enemy_boss:
        # 空いているマスを探す
        empty_slots = [k for k, v in st.session_state.grid_enemy.items() if v is None]
        # 確率で召喚（空きマスがあり、かつボスが生きていれば）
        if empty_slots and random.random() < 0.3: # 30%の確率で召喚
            target_slot = random.choice(empty_slots)
            summon = random.choice(st.session_state.summonable_enemies).copy()
            summon["max_hp"] = summon["hp"]
            st.session_state.grid_enemy[target_slot] = summon
            st.session_state.battle_log.append(f"👹 ボスが新たな敵を呼び出した！")
    # 敵の攻撃
    for pos, enemy in st.session_state.grid_enemy.items():
        if enemy and enemy["hp"] > 0:
            # 生きている味方を探す（本来は配置依存にするが簡易的にランダム）
            alive_allies = [k for k, v in st.session_state.grid_ally.items() if v and v["hp"] > 0]
            if alive_allies:
                # 配置の右列(前衛)に誰かいれば優先される簡易ターゲット選定
                front_line = [k for k in alive_allies if k.endswith(",2")]
                target_pos = random.choice(front_line) if front_line else random.choice(alive_allies)
                
                char = st.session_state.grid_ally[target_pos]
                stats = get_total_stats(char)
                damage = max(1, enemy["atk"] - stats["df"])
                if enemy.get("skill") == "鉄壁の構え" and enemy.get("skill_duration", 0) > 0:
                    damage //= 2 # ダメージを半減
                    log.append(f"🛡️ 鉄壁の構えでダメージ軽減！")
                # 物理反射の処理
                elif char["skill"] == "物理反射" and char.get("skill_duration", 0) > 0:
                    reflect_dmg = damage // 2
                    enemy["hp"] -= reflect_dmg
                    log.append(f"🪞 ゴライアスの物理反射！{enemy['name']} に {reflect_dmg} ダメージ！")
                char["hp"] -= damage
                log.append(f"👹 {enemy['name']} が {char['name']} に {damage} ダメージ！")
                if char["hp"] <= 0:
                    log.append(f"💀 {char['name']} が倒れた…")
    # 修正後：以下のように「if char:」で存在確認をします
    for char in st.session_state.grid_ally.values():
        if char:  # キャラクターが存在する場合のみ処理する
            duration = char.get('df_buff_duration', 0)
            
            if duration > 0:
                char['df_buff_duration'] -= 1
                if char['df_buff_duration'] == 0:
                    char['df'] -= 5  # バフ解除
                    log.append(f"ℹ️ {char['name']} の陣形バフが切れた。")
    st.session_state.battle_log.extend(log)
    

    
    # 勝敗判定
    allies_alive = any(v["hp"] > 0 for v in st.session_state.grid_ally.values() if v)
    enemies_alive = any(v["hp"] > 0 for v in st.session_state.grid_enemy.values() if v)
    
    if not enemies_alive:
        st.session_state.battle_log.append("🎉 戦闘に勝利した！")
        return "WIN"
    elif not allies_alive:
        st.session_state.battle_log.append("❌ 全滅した...")
        return "LOSE"
    return "CONTINUE"

# --- 4. 画面描画ロジック ---

# 4-1. キャラクター選択画面
if st.session_state.phase == "CHARACTER_SELECT":
    st.title("🛡️ ローグライクRPG：パーティー結成")
    st.write("4人の冒険者を選んでください。")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        blocker = st.selectbox("ブロッカー (1人)", [c["name"] for c in CHARACTER_POOL["ブロッカー"]])
    with col2:
        attackers = st.multiselect("アタッカー (2人選択)", [c["name"] for c in CHARACTER_POOL["アタッカー"]], max_selections=2)
    with col3:
        healer = st.selectbox("ヒーラー (1人)", [c["name"] for c in CHARACTER_POOL["ヒーラー"]])
        
    if st.button("このパーティーで出発する"):
        if len(attackers) != 2:
            st.error("アタッカーは必ず2人選んでください！")
        else:
            # パーティー構築
            selected_chars = []
            for pool in CHARACTER_POOL.values():
                for c in pool:
                    if c["name"] in [blocker, healer] or c["name"] in attackers:
                        # 参照切り離しのためコピー
                        char_copy = c.copy()
                        char_copy["max_hp"] = c["hp"]
                        # 【重要】ここでスロットを確実に初期化する
                        char_copy["weapon_slots"] = [None, None]
                        char_copy["armor_slot"] = None
                        selected_chars.append(char_copy)
            st.session_state.party = selected_chars
            
            # デフォルト配置（前衛にブロッカー、後衛にその他）
            for i, char in enumerate(selected_chars):
                if char["role"] == "ブロッカー":
                    st.session_state.grid_ally["1,2"] = char # 中央列・前衛
                elif i == 1: st.session_state.grid_ally["0,0"] = char
                elif i == 2: st.session_state.grid_ally["1,0"] = char
                else: st.session_state.grid_ally["2,0"] = char
                    
            st.session_state.current_choices = generate_choices()
            st.session_state.phase = "EXPLORE"
            st.rerun()

# 4-2. 探索画面
elif st.session_state.phase == "EXPLORE":
    st.title(f"🗺️ エリア {st.session_state.area} / 5  ({st.session_state.event_count}/10 進捗)")
    
    # ステータス表示
    st.subheader("現在のパーティー")
    cols = st.columns(4)
    for i, char in enumerate(st.session_state.party):
        with cols[i]:
            st.metric(label=f"{char['name']} ({char['role']})", value=f"HP: {char['hp']}/{char['max_hp']}", delta=f"ATK:{char['atk']} / DF:{char['df']}")

    st.divider()
    
    # イベント選択
    if st.session_state.event_count < 10:
        st.subheader("次の行動を選択してください")
        ecols = st.columns(3)
        for i, choice in enumerate(st.session_state.current_choices):
            with ecols[i]:
                if st.button(f"✨ {choice}イベントを発生させる", key=f"choice_{i}", use_container_width=True):
                    st.session_state.event_count += 1
                    if choice == "戦闘":
                        init_enemy(is_boss=False)
                        st.session_state.battle_log = ["通常戦闘が開始された！"]
                        st.session_state.phase = "BATTLE"
                    else:
                        # 戦闘以外のイベント（簡易処理）
                        st.success(f"{choice}に成功！パーティーが強化/回復された。")
                        for c in st.session_state.party:
                            if choice == "回復": c["hp"] = min(c["max_hp"], c["hp"] + 20)
                            if choice == "装備獲得":
                                st.session_state.phase = "SHOP"
                            if choice == "スキル獲得": c["atk"] += 2
                        st.session_state.current_choices = generate_choices()
                    st.rerun()
    else:
        st.warning("⚠️ エリアボスが待ち受けています！準備を整えてください。")
        if st.button("🔥 エリアボス戦に挑む", use_container_width=True, type="primary"):
            init_enemy(is_boss=True)
            st.session_state.current_enemy_boss = True
            st.session_state.battle_log = [f"エリア {st.session_state.area} のボスが現れた！"]
            st.session_state.phase = "BATTLE"
            st.rerun()

# 4-3. 戦闘画面（配置 ＆ バトルログ）
elif st.session_state.phase == "BATTLE":
    st.title("⚔️ 3×3 タクティカルバトル")
    
    # 配置カスタマイズエリア
    with st.expander("🔄 戦闘前の陣形配置を変更する"):
        st.write("味方を好きなグリッドにドラッグ...の代わりにプルダウンで再配置できます。右列が前衛です。")
        # 簡易的な再配置UI
        for char in st.session_state.party:
            if char["hp"] > 0:
                # 現在の位置を探す
                curr_pos = [k for k, v in st.session_state.grid_ally.items() if v and v["name"] == char["name"]]
                curr_val = curr_pos[0] if curr_pos else "未配置"
                
                options = ["0,0","0,1","0,2","1,0","1,1","1,2","2,0","2,1","2,2"]
                new_pos = st.selectbox(f"{char['name']} の位置 (行, 列)", options, index=options.index(curr_val) if curr_val in options else 0, key=f"pos_{char['name']}")
                
                # 配置換えロジック
                if curr_val != "未配置":
                    st.session_state.grid_ally[curr_val] = None
                st.session_state.grid_ally[new_pos] = char

    # 3x3 グリッドの可視化
    col_left, col_right = st.columns(2)
    
    # 3x3グリッド描画部（味方陣営）
    with col_left:
        st.subheader("🔵 味方陣営 (左:後衛 / 右:前衛)")
        for r in range(3):
            cols = st.columns(3)
            for c in range(3):
                cell = st.session_state.grid_ally[f"{r},{c}"]
                with cols[c]:
                    if cell:
                        display_character_card(cell, is_ally=True) # 自作関数でスマートに表示
                    else:
                        st.markdown("<div style='text-align:center;color:#ccc;border:1px dashed #ccc;padding:30px 0;border-radius:5px;'>（空）</div>", unsafe_allow_html=True)

    with col_right:
        st.subheader("🔴 敵陣営 (左:前衛 / 右:後衛)")
        for r in range(3):
            cols = st.columns(3)
            for c in range(3):
                cell = st.session_state.grid_enemy[f"{r},{c}"]
                with cols[c]:
                    if cell:
                        display_character_card(cell, is_ally=False) # 自作関数でスマートに表示
                    else:
                        
                        st.markdown("<div style='text-align:center;color:#ccc;border:1px dashed #ccc;padding:30px 0;border-radius:5px;'>（空）</div>", unsafe_allow_html=True)
    st.divider()
    
    # バトル進行ボタン
    st.subheader("バトルログ")
    for log in st.session_state.battle_log[-5:]: # 直近5件を表示
        st.write(log)
        
    if st.button("⚔️ ターンを進める", use_container_width=True, type="primary"):
        result = run_battle_turn()
        if result == "WIN":
            st.success("勝利！")
            # --- 経験値と資金の獲得 ---
            gain_exp = 50 * st.session_state.area
            gain_gold = 100 * st.session_state.area
            st.session_state.exp += gain_exp
            st.session_state.gold += gain_gold
            st.write(f"🎉 経験値 {gain_exp} と 資金 {gain_gold} を獲得！")
            
            # --- レベルアップ判定 ---
            if st.session_state.exp >= (st.session_state.level * 100):
                st.session_state.level += 1
                st.session_state.exp = 0
                # パーティー全員のステータス上昇
                for char in st.session_state.party:
                    char["max_hp"] += 10
                    char["hp"] = char["max_hp"]
                    char["atk"] += 2
                    char["df"] += 1
                st.balloons()
                st.success(f"レベルアップ！全員の能力が強化された！")
            if st.session_state.current_enemy_boss:
                if st.session_state.area == 5:
                    st.session_state.phase = "CLEAR"
                else:
                    st.session_state.area += 1
                    st.session_state.event_count = 0
                    st.session_state.current_enemy_boss = False
                    st.session_state.phase = "EXPLORE"
                    st.session_state.current_choices = generate_choices()
            else:
                st.session_state.phase = "EXPLORE"
                st.session_state.current_choices = generate_choices()
        elif result == "LOSE":
            st.session_state.phase = "GAME_OVER"
        st.rerun()
elif st.session_state.phase == "SHOP":
    st.title("💰 装備ショップ")
    st.write(f"所持金: {st.session_state.gold} G")
    # （既存の「現在のパーティー装備」表示部分をここに置く）
    # 3. 現在の装備状況の表示
    st.subheader("現在のパーティー装備")
    
    # キャラクターごとの装備状況を表示
    for char in st.session_state.party:
        with st.expander(f"{char['name']} の装備状況"):
            # 武器の表示
            weapons = char.get("weapon_slots", [None, None])
            for i, weapon in enumerate(weapons):
                w_name = weapon['name'] if weapon else "なし"
                st.write(f"武器スロット{i+1}: {w_name}")
            
            # 防具の表示
            armor = char.get("armor_slot")
            a_name = armor['name'] if armor else "なし"
            st.write(f"防具: {a_name}")
            
            # 現在のステータス補正値も併せて表示すると親切
            stats = get_total_stats(char)
            st.caption(f"合計攻撃力: {stats['atk']} / 合計防御力: {stats['df']}")
            
    # 販売リスト（購入と装着を同時に行うUI）
    st.subheader("販売リスト")
    for i, item in enumerate(st.session_state.shop_items):
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{item['name']}** ({item['price']}G)")
            with col2:
                # keyにアイテム名を含めて一意にする
                target_char = st.selectbox(
                    f"装着先を選択", 
                    st.session_state.party, 
                    format_func=lambda c: c['name'],
                    key=f"char_select_{item['name']}_{i}" 
                )
            with col3:
                # keyにアイテム名を含めて一意にする
                if st.button("購入＆装着", key=f"buy_btn_{item['name']}_{i}"):
                    if st.session_state.gold >= item['price']:
                        st.session_state.gold -= item['price']
                        
                        new_item = item.copy() 
                        
                        if item['type'] == 'weapon':
                            # スロット1を優先、空いていれば装着
                            if target_char['weapon_slots'][0] is None:
                                target_char['weapon_slots'][0] = new_item
                            else:
                                target_char['weapon_slots'][1] = new_item
                        else:
                            target_char['armor_slot'] = new_item
                            
                        st.success(f"{target_char['name']} に {item['name']} を装着！")
                        st.rerun() 
                    else:
                        st.error("資金不足です！")

    st.divider()
    
    if st.button("探索に戻る"):
        st.session_state.phase = "EXPLORE"
        st.rerun()
# 4-4. ゲームオーバー / クリア
elif st.session_state.phase == "GAME_OVER":
    st.title("💀 GAME OVER")
    st.error("パーティーが全滅しました。")
    if st.button("タイトルに戻る"):
        st.session_state.clear()
        st.rerun()

elif st.session_state.phase == "CLEAR":
    st.title("👑 GAME CLEAR!")
    st.balloons()
    st.success("おめでとうございます！5つのエリアを全て踏破しました！")
    if st.button("もう一度遊ぶ"):
        st.session_state.clear()
        st.rerun()

import streamlit as st
import random
import pandas as pd
import os
# ページ設定
st.set_page_config(page_title="Streamlit Roguelike", layout="wide")

# --- 1. データ定義 ---
CHARACTER_POOL = {
    "ブロッカー": [
        {"name": "聖騎士アルタニア", "hp": 150, "atk": 10, "df": 20, "role": "ブロッカー", "image": "assets/altania.png"},
        {"name": "鉄壁のゴライアス", "hp": 180, "atk": 8, "df": 25, "role": "ブロッカー", "image": "assets/golaias.png"}
    ],
    "アタッカー": [
        {"name": "魔術師エルザ", "hp": 80, "atk": 25, "df": 5, "role": "アタッカー", "image": "assets/elsa.png"},
        {"name": "暗殺者レイジ", "hp": 90, "atk": 22, "df": 8, "role": "アタッカー", "image": "assets/reizi.png"},
        {"name": "狩人シルフ", "hp": 95, "atk": 20, "df": 10, "role": "アタッカー", "image": "assets/silf.png"},
        {"name": "狂戦士バルド", "hp": 120, "atk": 18, "df": 12, "role": "アタッカー", "image": "assets/vald.png"},
        {"name": "侍ムサシ", "hp": 100, "atk": 24, "df": 9, "role": "アタッカー", "image": "assets/musasi.png"},
        {"name": "竜騎士ジーク", "hp": 110, "atk": 21, "df": 14, "role": "アタッカー", "image": "assets/jeek.png"}
    ],
    "ヒーラー": [
        {"name": "司祭セシリア", "hp": 85, "atk": 8, "df": 7, "role": "ヒーラー", "heal": 20, "image": "assets/sesiria.png"},
        {"name": "吟遊詩人アリア", "hp": 90, "atk": 10, "df": 10, "role": "ヒーラー", "heal": 15, "image": "assets/alia.png"}
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
            {"name": "オーク", "hp": 45, "atk": 12, "df": 5, "image": "assets/orc.png"},
            {"name": "スケルトンソルジャー", "hp": 30, "atk": 15, "df": 2, "image": "assets/skeleton.png"},
            {"name": "迷い子のゴースト", "hp": 40, "atk": 10, "df": 4, "image": "assets/ghost.png"},
            {"name": "巨大毒サソリ", "hp": 55, "atk": 16, "df": 6, "image": "assets/scorpion.png"},
            {"name": "マインミミック", "hp": 60, "atk": 8, "df": 12, "image": "assets/mimic.png"}
        ],
        "boss": {"name": "影の支配者リッチ", "hp": 300, "atk": 25, "df": 12, "image": "assets/lich_boss.png"}
    }, # エリア2〜5も同様にパラメータと画像パスを設定
    3: {
        "normal": [
            {"name": "マグモスライム", "hp": 45, "atk": 12, "df": 5, "image": "assets/magma_slime.png"},
            {"name": "ファイアバード", "hp": 30, "atk": 15, "df": 2, "image": "assets/fire_bird.png"},
            {"name": "サラマンダー", "hp": 40, "atk": 10, "df": 4, "image": "assets/salamander.png"},
            {"name": "ストーンゴーレム", "hp": 55, "atk": 16, "df": 6, "image": "assets/golem.png"},
            {"name": "ラヴァインプ", "hp": 60, "atk": 8, "df": 12, "image": "assets/lava_imp.png"}
        ],
        "boss": {"name": "古代の重戦車", "hp": 300, "atk": 25, "df": 12, "image": "assets/stone_boss.png"}
    }, 
    4: {
        "normal": [
            {"name": "マーダーラプトル", "hp": 45, "atk": 12, "df": 5, "image": "assets/raptor.png"},
            {"name": "アポカリプスウィスプ", "hp": 30, "atk": 15, "df": 2, "image": "assets/wisp.png"},
            {"name": "ガーゴイル", "hp": 40, "atk": 10, "df": 4, "image": "assets/gargoyle.png"},
            {"name": "テンタクルウォーター", "hp": 55, "atk": 16, "df": 6, "image": "assets/tentacle.png"},
            {"name": "ミストシーフ", "hp": 60, "atk": 8, "df": 12, "image": "assets/thief.png"}
        ],
        "boss": {"name": "瀑布の妖姫セイレーン", "hp": 300, "atk": 25, "df": 12, "image": "assets/siren_boss.png"}
    }, 
    5: {
        "normal": [
            {"name": "ドラゴニュート", "hp": 45, "atk": 12, "df": 5, "image": "assetsdragoniut.png"},
            {"name": "キマイラ", "hp": 30, "atk": 15, "df": 2, "image": "assets/chimera.png"},
            {"name": "アークデーモン", "hp": 40, "atk": 10, "df": 4, "image": "assets/demon.png"},
            {"name": "アーマードナイト", "hp": 55, "atk": 16, "df": 6, "image": "assets/armored_knight.png"},
            {"name": "イビルアイ", "hp": 60, "atk": 8, "df": 12, "image": "assets/evil_eye.png"}
        ],
        "boss": {"name": "終焉の紅蓮竜", "hp": 300, "atk": 25, "df": 12, "image": "assets/dragon_boss.png"}
    }
}
EVENT_TYPES = ["戦闘", "装備獲得", "アイテム獲得", "回復", "スキル獲得", "特殊遭遇"]
def display_character_card(cell, is_ally):
    # 画像が存在すれば表示、なければダミーの箱を表示
    if os.path.exists(cell["image"]):
        st.image(cell["image"], use_container_width=True)
    else:
        placeholder_color = "🔵" if is_ally else "🔴"
        st.markdown(f"<div style='text-align:center;font-size:40px;background:#eee;padding:10px;border-radius:5px;'>{placeholder_color}</div>", unsafe_allow_html=True)
    
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

# --- 3. 関数定義 ---
def generate_choices():
    return random.sample(EVENT_TYPES, 3)

def init_enemy(is_boss=False):
    st.session_state.grid_enemy = {f"{r},{c}": None for r in range(3) for c in range(3)}
    num_enemies = 1 if is_boss else random.randint(1, 3)
    
    for _ in range(num_enemies):
        r, c = random.randint(0, 2), random.randint(0, 2)
        if is_boss:
            st.session_state.grid_enemy[f"{r},{c}"] = {"name": f"エリア{st.session_state.area}ボス", "hp": 300 + st.session_state.area*100, "atk": 25, "df": 15, "max_hp": 300}
            break
        else:
            st.session_state.grid_enemy[f"{r},{c}"] = {"name": f"ゴブリン", "hp": 40 + st.session_state.area*10, "atk": 12, "df": 5, "max_hp": 50}

def run_battle_turn():
    # 簡易自動戦闘シミュレーションロジック
    log = []
    # 味方の攻撃
    for pos, char in st.session_state.grid_ally.items():
        if char and char["hp"] > 0:
            # 生きている敵を探す
            alive_enemies = [k for k, v in st.session_state.grid_enemy.items() if v and v["hp"] > 0]
            if alive_enemies:
                target_pos = random.choice(alive_enemies)
                enemy = st.session_state.grid_enemy[target_pos]
                damage = max(1, char["atk"] - enemy["df"])
                enemy["hp"] -= damage
                log.append(f"⚔️ {char['name']} が {enemy['name']} に {damage} ダメージ！")
                if enemy["hp"] <= 0:
                    log.append(f"💥 {enemy['name']} を倒した！")
    
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
                damage = max(1, enemy["atk"] - char["df"])
                char["hp"] -= damage
                log.append(f"👹 {enemy['name']} が {char['name']} に {damage} ダメージ！")
                if char["hp"] <= 0:
                    log.append(f"💀 {char['name']} が倒れた…")

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
                            if choice == "装備獲得": c["df"] += 2
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
                        st.text_area("", "（空）", height=80, disabled=True, key=f"e_{r}_{c}")
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

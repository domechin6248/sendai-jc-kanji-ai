import streamlit as st
import docx
import google.generativeai as genai
import os

# 1. ページ設定：監事の品格を表すデザイン
st.set_page_config(page_title="川内JC 監事審査AI", page_icon="⚖️", layout="wide")
st.title("⚖️ 2026年度 川内JC 監事専用・事業計画分析システム")
st.write("AIが計画書を読み込み、論理の整合性と改善案を提示します。")

# 2. APIキーの設定（サイドバー）
with st.sidebar:
    st.header("🔑 初期設定")
    api_key = st.text_input("Gemini API Keyを入力してください", type="password")
    st.info("APIキーは Google AI Studio で取得したものを入力してください。")
    if api_key:
        genai.configure(api_key=api_key)

# 3. 監事の思考を反映した分析関数
def analyze_with_ai(text):
    # 軽量で高速なモデルを使用
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 監事の視点を定義するプロンプト
    prompt = f"""
    あなたは川内青年会議所（JC）の「監事」です。36歳の不動産業経営者という背景を持ち、
    実務に厳しく、論理の整合性を最も重視します。
    以下の事業計画書のテキストを読み、監事講評を作成してください。

    【審査のポイント】
    1. 事業背景：薩摩川内市の現状や課題が具体的か？客観的データに基づいているか？
    2. 事業目的：背景の課題を解決するための「着地点」として妥当か？
    3. 事業内容：目的達成のために最短距離の手法か？メンバーの負担やコストは適正か？
    4. 検証方法：事業の成果を数値や事実で客観的に証明できるか？

    【出力形式】
    ・各項目（背景・目的・内容・検証）ごとの「現状分析」と「具体的アドバイス」
    ・全体の「一本筋」が通っているかの判定（合格 ／ 要再考）
    ・監事としての、厳しいながらもLOMを想う愛のある総評

    【計画書テキスト】
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI分析中にエラーが発生しました。APIキーが正しいか確認してください。: {str(e)}"

# 4. Wordファイルからテキストを抽出
def get_text_from_docx(file):
    doc = docx.Document(file)
    # 空行を除いてテキストを結合
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# 5. メイン画面の処理
uploaded_file = st.file_uploader("審査する計画書(Word)をドロップしてください", type=["docx"])

if uploaded_file:
    if not api_key:
        st.warning("左側のサイドバーにAPIキーを入力してください。")
    else:
        # ファイルから文字を読み出す
        try:
            text_content = get_text_from_docx(uploaded_file)
            
            if st.button("監事審査を開始する"):
                with st.spinner("監事が内容を精査中... 厳しい意見が出るかもしれません。"):
                    result = analyze_with_ai(text_content)
                    st.markdown("---")
                    st.header("📢 監事審査結果（AI講評）")
                    st.markdown(result)
                    
                    # 結果を保存したい場合のためのダウンロードボタン
                    st.download_button(
                        label="審査結果を保存",
                        data=result,
                        file_name="監事審査結果.txt",
                        mime="text/plain"
                    )
        except Exception as e:
            st.error(f"ファイルの読み込みに失敗しました: {e}")

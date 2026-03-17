import streamlit as st
import docx
import google.generativeai as genai
import os

# 1. ページ設定
st.set_page_config(page_title="川内JC 監事審査AI", page_icon="⚖️", layout="wide")
st.title("⚖️ 2026年度 川内JC 監事専用・事業計画分析システム")

# 2. APIキーの設定
with st.sidebar:
    st.header("🔑 初期設定")
    api_key = st.text_input("Gemini API Keyを入力してください", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# 3. 分析実行関数（モデルを順番に試す「バックアップ機能」付き）
def analyze_with_ai(text):
    # 試すモデルのリスト（最新から順に）
    models_to_try = [
        'gemini-1.5-flash-latest', 
        'gemini-1.5-pro-latest', 
        'gemini-pro'
    ]
    
    prompt = f"""
    あなたは川内青年会議所（JC）の「監事」です。36歳の不動産業経営者という背景を持ち、
    論理の整合性を最も重視します。以下の事業計画書を審査してください。
    
    【審査ポイント】背景・目的・内容・検証の「一本筋」が通っているか。
    【計画書テキスト】
    {text}
    """

    last_error = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue # 次のモデルを試す
            
    return f"全モデルでエラーが発生しました。APIキーの権限不足の可能性があります。\n詳細: {last_error}"

# 4. Word読み込み
def get_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# 5. メイン画面
uploaded_file = st.file_uploader("審査する計画書(Word)をアップロード", type=["docx"])

if uploaded_file:
    if not api_key:
        st.warning("左側のサイドバーにAPIキーを入力してください。")
    else:
        try:
            text_content = get_text_from_docx(uploaded_file)
            if st.button("監事審査を開始する"):
                with st.spinner("AI監事が精査中...（モデルを順次テストしています）"):
                    result = analyze_with_ai(text_content)
                    st.markdown("---")
                    st.header("📢 監事審査結果")
                    st.markdown(result)
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")

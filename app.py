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

# 3. 分析実行関数（モデル指定を最も標準的なものに変更）
def analyze_with_ai(text):
    # 'gemini-1.5-flash' が見つからない場合、'gemini-pro' を試す設定にします
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        あなたは川内青年会議所（JC）の「監事」です。36歳の不動産業経営者という背景を持ち、
        論理の整合性を最も重視します。以下の事業計画書を審査してください。
        
        【審査のポイント】
        1. 背景：課題が具体的か。
        2. 目的：背景を解決するゴールか。
        3. 内容：手法が妥当か。
        4. 検証：成果を数値で証明できるか。

        【計画書】
        {text}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # もしflashモデルが使えない場合、古い標準モデルで再試行します
        try:
            model_alt = genai.GenerativeModel('gemini-pro')
            response = model_alt.generate_content(prompt)
            return response.text
        except:
            return f"エラー詳細: {str(e)}\n\n※Google AI Studioで'Gemini 1.5 Flash'の利用が許可されているか確認してください。"

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
                with st.spinner("AI監事が精査中..."):
                    result = analyze_with_ai(text_content)
                    st.markdown("---")
                    st.header("📢 監事審査結果")
                    st.markdown(result)
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")

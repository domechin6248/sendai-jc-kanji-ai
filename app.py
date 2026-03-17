import streamlit as st
import docx
import requests
import json

# 1. ページ設定
st.set_page_config(page_title="川内JC 監事審査AI", page_icon="⚖️")
st.title("⚖️ 2026年度 川内JC 監事専用・事業計画分析システム")

# 2. APIキーの設定
with st.sidebar:
    st.header("🔑 初期設定")
    api_key = st.text_input("Gemini API Keyを入力してください", type="password")

# 3. 分析実行関数（ライブラリを使わず、直接Googleにリクエストを送る方法）
def analyze_with_ai_direct(text, key):
    # GoogleのAPIへ直接アクセスするURL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{
                "text": f"あなたは川内JCの監事（36歳・不動産業）です。以下の計画書を論理的に審査し、背景・目的・手法・検証の整合性を講評してください。\n\n{text}"
            }]
        }]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"エラーが発生しました（ステータスコード: {response.status_code}）\n詳細: {response.text}"

# 4. Word読み込み
def get_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# 5. メイン画面
uploaded_file = st.file_uploader("審査する計画書(Word)をアップロード", type=["docx"])

if uploaded_file and api_key:
    try:
        text_content = get_text_from_docx(uploaded_file)
        if st.button("監事審査を開始する"):
            with st.spinner("AI監事が精査中..."):
                result = analyze_with_ai_direct(text_content, api_key)
                st.markdown("---")
                st.header("📢 監事審査結果")
                st.markdown(result)
    except Exception as e:
        st.error(f"ファイル読み込みエラー: {e}")

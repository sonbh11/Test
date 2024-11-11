from flask import Flask, request, jsonify, render_template
from LastTest import general_conversation_chain  # LastTest.py의 함수 사용

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    # HTML 렌더링
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # 클라이언트에서 질문 받기
        data = request.json
        question = data.get("question", "")

        # 질문 처리 함수 호출
        response = general_conversation_chain(question)

        # JSON 응답 반환
        return jsonify({"response": response}), 200
    except Exception as e:
        # 에러 처리
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

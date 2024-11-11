from dotenv import load_dotenv
from langchain import hub

from langchain_community.vectorstores import FAISS
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_teddynote import logging
from langchain.prompts import PromptTemplate  # 커스텀 프롬프트를 위한 추가 import


load_dotenv()

# file_path='data/yu_history.pdf'
# loader = PyPDFLoader(file_path)
#
# docs = loader.load()
#
# # 단계 2: 문서 분할(Split Documents)
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#
# splits = text_splitter.split_documents(docs)

# 단계 3: 임베딩 & 벡터스토어 생성(Create Vectorstore)
# 벡터스토어를 생성합니다.
# vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# vectorstore.save_local('data/vectorstore/YU_HISTORY')

db1 = FAISS.load_local('data/vectorstore/YU_CSE_INFO', OpenAIEmbeddings(), allow_dangerous_deserialization=True)
db2 = FAISS.load_local('data/vectorstore/YU_HISTORY', OpenAIEmbeddings(), allow_dangerous_deserialization=True)

db1.merge_from(db2)


# 단계 4: 검색(Search)
# 뉴스에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = db1.as_retriever()

# 단계 5: 프롬프트 생성(Create Prompt)
# 프롬프트를 생성합니다.
prompt = hub.pull("rlm/rag-prompt")

# 커스텀 프롬프트 정의
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
당신은 친절하고 지적인 AI 어시스턴트입니다. 
사용자가 질문한 내용이 벡터 데이터베이스에서 검색되면 관련된 정보를 요약해서 제공하세요. 
검색되지 않거나 질문이 모호할 경우, 질문의 의도를 분석하고 정중하게 다시 질문을 요청하세요.
또한 벡터 데이터베이스에서 검색되지 않는 당신이 답변할수있는 답변을 해주세요. 

[컨텍스트]:
{context}

[질문]:
{question}

[답변]:
"""
)

# 단계 6: 언어모델 생성(Create LLM)
# 모델(LLM) 을 생성합니다.

#답변 스트리밍을 위한 함수
class StreamCallback(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(token, end="", flush=True)

# llm 객체 생성
llm = ChatOpenAI(
    model_name="gpt-4-turbo-preview",
    temperature=0.5,
    streaming=True,
    callbacks=[StreamCallback()],
)

def format_docs(docs):
    # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
    return "\n\n".join(doc.page_content for doc in docs)


# 단계 7: 체인 생성(Create Chain)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | custom_prompt
    | llm
    | StrOutputParser()
)

# def general_conversation_chain(question):
#     try:
#         # 벡터 DB 검색
#         response = rag_chain.invoke(question)
#     except Exception:
#         # 벡터 DB 검색 실패 시 일반적 응답 생성
#         response = llm.invoke(f"다음 질문에 답해주세요: {question}")
#     return response

# def general_conversation_chain(question):
#     try:
#         # 벡터 DB에서 검색
#         response = rag_chain.invoke(question)
#     except Exception:
#         response = llm.invoke(f"{question}")
#     return response


def general_conversation_chain(question):
    try:
        # 벡터 데이터베이스에서 문서 검색 및 포맷
        # 디버깅용 출력 (필요 시 삭제 가능)
        # print("[DEBUG] Retrieved Context:", context)
        # 체인 실행
        response = rag_chain.invoke(question)
    except Exception as e:
        response = llm.invoke(f"{question}")
    return response

# # 단계 8: 체인 실행(Run Chain)
if __name__ == "__main__":
    while True:
        question = input("[HUMAN]: ")
        if question.lower() in ["종료", "대화종료"]:
            print("\n 대화종료. ")
            break
        print("[AI]: ", end="")
        general_conversation_chain(question)
        print()
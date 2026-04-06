import streamlit as st
import requests
import json

#               ВАШИ ДАННЫЕ
API_KEY = "AQVNxxL8F0PWwxZk6dgWmTcb8dpF2MK7U9UCPzZl"
FOLDER_ID = "b1gqq8ef2a242jjujuj8"


st.set_page_config(page_title="AI Репетитор: ВПР и Олимпиады", page_icon="📚", layout="wide")


def ask_yandexgpt(messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Authorization": f"Api-Key {API_KEY}", "Content-Type": "application/json"}
    system_text = ""
    chat_history = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            chat_history.append({"role": msg["role"], "text": msg["content"]})
    request_body = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"stream": False, "temperature": 0.7, "maxTokens": 1000},
        "messages": [{"role": "system", "text": system_text}, *chat_history]
    }
    try:
        response = requests.post(url, headers=headers, json=request_body)
        response.raise_for_status()
        return response.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        st.error(f"Ошибка YandexGPT: {e}")
        if 'response' in locals():
            st.error(f"Ответ сервера: {response.text}")
        return "Ошибка. Попробуйте позже."


def get_system_prompt(subject, exam_type, grade):
    return f"""Ты — репетитор по {subject} для {grade} класса. Готовишь к {exam_type}.
Правила: дружелюбно, по одному заданию, проверяй ответы, не давай готовое решение, подсказывай.
Задания должны соответствовать уровню {exam_type} для {grade} класса.
Общайся на русском."""


# Инициализация
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_subject" not in st.session_state:
    st.session_state.current_subject = "Математика"
if "current_grade" not in st.session_state:
    st.session_state.current_grade = 7
if "current_exam_type" not in st.session_state:
    st.session_state.current_exam_type = "ВПР"

# Боковая панель с динамическим выбором класса
with st.sidebar:
    st.header("📌 Настройки")
    subject = st.selectbox("Предмет", ["Математика", "Русский язык", "Физика", "Астраномия", "Химия", "Биология", "История"])
    exam_type = st.radio("Тип", ["ВПР", "Олимпиада"])

    # ВПР только для 4-8 классов
    if exam_type == "ВПР":
        available_grades = list(range(4, 9))  # 4,5,6,7,8
        default_grade = 7
    else:
        available_grades = list(range(4, 12))  # 4,5,6,7,8,9,10,11
        default_grade = 7

    grade = st.selectbox("Класс", available_grades, index=available_grades.index(default_grade))

    if st.button("🔄 Начать новый диалог"):
        st.session_state.messages = []
        st.session_state.current_subject = subject
        st.session_state.current_grade = grade
        st.session_state.current_exam_type = exam_type
        st.rerun()

# Обновление настроек
if (st.session_state.current_subject != subject or
        st.session_state.current_grade != grade or
        st.session_state.current_exam_type != exam_type):
    st.session_state.current_subject = subject
    st.session_state.current_grade = grade
    st.session_state.current_exam_type = exam_type

st.title("📚 Репетитор для подготовки к ВПР и олимпиадам")
st.markdown(
    f"**Предмет:** {st.session_state.current_subject}  |  **Тип:** {st.session_state.current_exam_type}  |  **Класс:** {st.session_state.current_grade}")

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Первое сообщение, если пусто
if len(st.session_state.messages) == 0:
    system_prompt = get_system_prompt(st.session_state.current_subject, st.session_state.current_exam_type,
                                      st.session_state.current_grade)
    first_request = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Дай первое задание."}]
    with st.chat_message("assistant"):
        with st.spinner("Готовлю задание..."):
            response = ask_yandexgpt(first_request)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Ввод пользователя
if prompt := st.chat_input("Напишите ответ или вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    system_prompt = get_system_prompt(st.session_state.current_subject, st.session_state.current_exam_type,
                                      st.session_state.current_grade)
    full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            response = ask_yandexgpt(full_messages)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
st.caption("YandexGPT. Репетитор для ВПР и олимпиад.")
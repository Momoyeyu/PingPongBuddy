import streamlit as st
import datetime
import os
from dotenv import load_dotenv

from pingpongbuddy.agents import PingPongAgent

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="友小智 - PingPongBuddy",
    page_icon="🏓",
    layout="centered"
)

# 标题
st.title("🏓 友小智 - PingPongBuddy")
st.subheader("乒乓球友约球智能助手")

# 初始化状态
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = PingPongAgent()

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 侧边栏 - 约球信息
with st.sidebar:
    st.header("约球信息")
    
    today = datetime.date.today()
    date = st.date_input("选择日期", today + datetime.timedelta(days=1))
    
    time = st.time_input("选择时间", datetime.time(14, 0))
    
    datetime_str = f"{date} {time.strftime('%H:%M')}"
    
    place = st.text_input("场地", "")
    
    if st.button("发起约球", disabled=not place):
        # 添加用户消息
        user_message = f"我想在 {datetime_str} 在 {place} 打乒乓球，请帮我找球友"
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # 获取智能体回复
        with st.spinner("正在寻找球友..."):
            response = st.session_state.agent.invoke(
                time=datetime_str,
                place=place
            )
        
        # 添加助手消息
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 刷新页面显示结果
        st.rerun()

# 聊天输入
if prompt := st.chat_input("和友小智聊聊..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)
    
    # 显示助手消息
    with st.chat_message("assistant"):
        response = st.session_state.agent.invoke(
            time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            place="默认场地"
        )
        st.write(response)
    
    # 添加助手消息到历史
    st.session_state.messages.append({"role": "assistant", "content": response})

# 页脚
st.markdown("---")
st.caption("友小智 - PingPongBuddy | 基于 Langchain 和 GLM-4-Flash")
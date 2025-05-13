import streamlit as st
import datetime
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在可以导入项目模块
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
    
    # 基本信息
    today = datetime.date.today()
    date = st.date_input("选择日期", today + datetime.timedelta(days=1))
    
    time = st.time_input("选择时间", datetime.time(14, 0))
    
    datetime_str = f"{date} {time.strftime('%H:%M')}"
    
    place = st.text_input("场地", "")
    
    # 高级选项（可折叠）
    show_advanced = st.checkbox("显示高级选项")
    
    skill_level = None
    opponent_count = None
    opponent_skill_level = None
    match_type = None
    additional_notes = None
    
    if show_advanced:
        with st.expander("高级约球选项", expanded=True):
            skill_level = st.selectbox(
                "我的技术水平", 
                options=["", "初级", "中级", "高级", "专业"],
                index=0
            )
            
            opponent_count = st.selectbox(
                "希望找几位球友", 
                options=["", "1", "2", "3", "4", "不限"],
                index=0
            )
            
            opponent_skill_level = st.selectbox(
                "希望球友的技术水平", 
                options=["", "不限", "初级", "中级", "高级", "专业"],
                index=0
            )
            
            match_type = st.selectbox(
                "比赛类型", 
                options=["", "友谊赛", "训练", "正式比赛", "教学"],
                index=0
            )
            
            additional_notes = st.text_area("备注", "", height=100)
    
    if st.button("发起约球", disabled=not place):
        # 构建用户消息
        user_message = f"我想在 {datetime_str} 在 {place} 打乒乓球"
        
        # 收集提供的高级选项
        advanced_options = []
        if skill_level:
            advanced_options.append(f"我的技术水平是{skill_level}")
        if opponent_count:
            advanced_options.append(f"希望找{opponent_count}个球友")
        if opponent_skill_level:
            advanced_options.append(f"对手技术水平在{opponent_skill_level}左右")
        if match_type:
            advanced_options.append(f"比赛类型为{match_type}")
        if additional_notes:
            advanced_options.append(f"备注：{additional_notes}")
        
        # 添加高级选项到消息
        if advanced_options:
            user_message += "，" + "，".join(advanced_options)
            
        # 添加到会话记录
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # 获取智能体回复
        with st.spinner("正在寻找球友..."):
            response = st.session_state.agent.invoke(
                input_text=user_message,
                time=datetime_str,
                place=place,
                skill_level=skill_level,
                opponent_count=opponent_count,
                opponent_skill_level=opponent_skill_level,
                match_type=match_type,
                additional_notes=additional_notes
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
        # 直接使用用户输入的文本调用智能体
        response = st.session_state.agent.invoke(input_text=prompt)
        st.write(response)
    
    # 添加助手消息到历史
    st.session_state.messages.append({"role": "assistant", "content": response})

# 页脚
st.markdown("---")
st.caption("友小智 - PingPongBuddy | 基于 Langchain 和 GLM-4-Flash")
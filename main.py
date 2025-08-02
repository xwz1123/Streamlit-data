import pandas as pd
import streamlit as st
from utils import dataframe_agent


def create_chart(input_data, chart_type):
    df_data = pd.DataFrame(input_data["data"], columns=input_data["columns"])
    df_data.set_index(input_data["columns"][0], inplace=True)
    if chart_type == "bar":
        st.bar_chart(df_data)
    elif chart_type == "line":
        st.line_chart(df_data)
    elif chart_type == "scatter":
        st.scatter_chart(df_data)

st.title("💡 数据分析智能工具 💡")

with st.sidebar:
    openai_api_key = st.text_input("请输入OpenAI API密钥：", type="password")
    st.markdown("[获取OpenAI API key](https://platform.openai.com/account/api-keys)")

data = st.file_uploader("上传你的数据文件（CSV/XLSX/XLS格式）：", type=["csv", "xlsx", "xls"])
if data:
    # 根据文件扩展名选择合适的读取方法
    file_extension = data.name.split(".")[-1].lower()

    try:
        if file_extension == "csv":
            st.session_state["df"] = pd.read_csv(data, encoding="gbk")
        elif file_extension in ["xlsx", "xls"]:
            # 读取Excel文件，默认读取第一个工作表
            st.session_state["df"] = pd.read_excel(data)

        # 显示原始数据
        with st.expander("原始数据"):
            st.dataframe(st.session_state["df"])

    except Exception as e:
        st.error(f"文件读取错误: {str(e)}")

query = st.text_area("请输入你关于以上表格的问题，或数据提取请求，或可视化要求（支持散点图、折线图、条形图）：")
button = st.button("生成回答")

if button and not openai_api_key:
    st.info("请输入你的OpenAI API密钥")
if button and "df" not in st.session_state:
    st.info("请先上传数据文件")
if button and openai_api_key and "df" in st.session_state:
    with st.spinner("AI正在思考中，请稍等..."):
        response_dict = dataframe_agent(openai_api_key, st.session_state["df"], query)
        if "answer" in response_dict:
            st.write(response_dict["answer"])
        if "table" in response_dict:
            st.table(pd.DataFrame(response_dict["table"]["data"],
                                  columns=response_dict["table"]["columns"]))
        if "bar" in response_dict:
            create_chart(response_dict["bar"], "bar")
        if "line" in response_dict:
            create_chart(response_dict["line"], "line")
        if "scatter" in response_dict:
            create_chart(response_dict["scatter"], "scatter")

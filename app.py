import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 页面配置
st.set_page_config(page_title="报表台", layout="wide")

# 初始化 session state
if 'df' not in st.session_state:
    st.session_state.df = None

# ===== 左侧 Sidebar =====
with st.sidebar:
    st.header("📁 文件上传")
    uploaded_file = st.file_uploader(
        "选择 CSV 或 Excel 文件",
        type=['csv', 'xlsx'],
        help="支持 .csv 和 .xlsx 格式"
    )
    
    if uploaded_file is not None:
        if uploaded_file.size > 100 * 1024 * 1024:
            st.error("文件过大，请上传小于 100MB 的文件")
            st.stop()                
        try:
            # 根据文件类型读取
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 检查是否为空
            if df.empty:
                st.error("⚠️ 文件为空，请上传包含数据的文件")
                st.session_state.df = None
            else:
                st.session_state.df = df
                st.success(f"✅ 成功读取 {len(df)} 行数据")
                
        except Exception as e:
            st.error(f"❌ 文件读取失败: {str(e)}")
            st.session_state.df = None

# ===== 主体 Main Area =====
st.title("📊 报表台")

df = st.session_state.df

if df is None:
    st.info("👆 请在左侧上传 CSV 或 Excel 文件开始使用")
else:
    # 查找数值列（只查找一次）
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # 若不存在数值列，显示警告并停止
    if not numeric_cols:
        st.warning("⚠️ 未找到数值列，无法绘制趋势图和导出报表")
    else:
        # 选择第一个数值列
        numeric_col = numeric_cols[0]
        avg_value = df[numeric_col].mean()
        
        # 生成 df_out，新增 value_diff 列
        df_out = df.copy()
        df_out['value_diff'] = df_out[numeric_col] - avg_value
        
        # === 数据总览卡片区 ===
        st.subheader("📈 数据总览")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("总记录数", len(df))
        
        with col2:
            st.metric("总列数", len(df.columns))
        
        with col3:
            st.metric(f"{numeric_col} 平均值", f"{avg_value:.2f}")
        
        st.divider()
        
        # === 趋势图 ===
        st.subheader("📉 趋势图")
        
        # 查找日期列
        date_col = None
        for col in df.columns:
            try:
                pd.to_datetime(df[col], errors='raise')
                date_col = col
                break
            except:
                continue
        
        try:
            # 准备数据
            plot_df = df_out.copy()
            
            # 设置 X 轴
            if date_col:
                plot_df[date_col] = pd.to_datetime(plot_df[date_col])
                x_col = date_col
            else:
                plot_df['行号'] = range(len(plot_df))
                x_col = '行号'
            
            # Y 轴使用 value_diff
            y_col = 'value_diff'
            
            # 绘制图表
            fig = px.line(
                plot_df,
                x=x_col,
                y=y_col,
                title=f"value_diff 趋势图",
                labels={x_col: x_col, y_col: 'value_diff'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"⚠️ 绘图失败: {str(e)}")
        
        # ===== 底部导出按钮 =====
        st.divider()
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            # 生成文件名
            filename = f"report_{datetime.now().strftime('%Y%m%d')}.csv"
            # 转换为 CSV
            csv_data = df_out.to_csv(index=False, encoding='utf-8')
            
            st.download_button(
                label="📥 导出报表",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                type="primary",
                use_container_width=True
            )



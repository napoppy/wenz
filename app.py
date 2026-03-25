import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from services.crawler import create_crawler
from services.data_processor import create_processor
from services.predictor import create_predictor
from services.pricing import create_pricing_service
from utils.exporters import create_exporter
from models.data_models import AnalysisResult
import config


st.set_page_config(
    page_title="智能投放分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        padding: 0.75rem 2rem;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'keyword' not in st.session_state:
        st.session_state.keyword = ""


def run_analysis(keyword: str, price_coefficient: float, platform: str, crawl_limit: int):
    crawler = create_crawler(platform=platform, use_mock=True)
    processor = create_processor()
    predictor = create_predictor()
    pricing_service = create_pricing_service(price_coefficient=price_coefficient)
    exporter = create_exporter()

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("正在搜索匹配账号...")
    progress_bar.progress(20)
    accounts = crawler.search_accounts_by_keyword(keyword, limit=crawl_limit)

    status_text.text("正在处理数据...")
    progress_bar.progress(40)
    for account in accounts:
        processor.process_account(account)

    status_text.text("正在预测下一篇文章数据...")
    progress_bar.progress(60)
    for account in accounts:
        predictor.predict_for_account(account)

    status_text.text("正在计算广告报价...")
    progress_bar.progress(80)
    accounts = pricing_service.calculate_for_accounts(accounts)

    accounts.sort(key=lambda x: x.estimated_read, reverse=True)

    result = AnalysisResult(
        keyword=keyword,
        accounts=accounts,
        total_accounts=len(accounts),
        total_articles=sum(a.article_count for a in accounts)
    )

    progress_bar.progress(100)
    status_text.text("分析完成!")

    return result


def display_accounts_table(accounts):
    df_data = [acc.to_dict() for acc in accounts]
    df = pd.DataFrame(df_data)

    df_display = df[[
        "account_name", "account_field", "avg_read_count",
        "avg_like_rate", "avg_comment_rate",
        "estimated_read", "price_standard", "price_min", "price_max"
    ]].copy()

    df_display.columns = [
        "账号名称", "领域", "平均阅读", "点赞率(%)",
        "评论率(%)", "预估阅读", "标准报价", "最低报价", "最高报价"
    ]

    df_display["平均阅读"] = df_display["平均阅读"].apply(lambda x: f"{x:,.0f}")
    df_display["预估阅读"] = df_display["预估阅读"].apply(lambda x: f"{x:,.0f}")
    df_display["点赞率(%)"] = df_display["点赞率(%)"].apply(lambda x: f"{x:.2f}")
    df_display["评论率(%)"] = df_display["评论率(%)"].apply(lambda x: f"{x:.2f}")
    df_display["标准报价"] = df_display["标准报价"].apply(lambda x: f"¥{x:,.0f}")
    df_display["最低报价"] = df_display["最低报价"].apply(lambda x: f"¥{x:,.0f}")
    df_display["最高报价"] = df_display["最高报价"].apply(lambda x: f"¥{x:,.0f}")

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

    return df


def display_charts(accounts):
    if not accounts:
        return

    df_data = [acc.to_dict() for acc in accounts[:10]]
    df = pd.DataFrame(df_data)

    tab1, tab2 = st.tabs(["账号对比", "数据分布"])

    with tab1:
        fig = px.bar(
            df,
            x="account_name",
            y=["estimated_read", "avg_read_count"],
            barmode="group",
            labels={"value": "阅读量", "account_name": "账号名称", "variable": "数据类型"},
            title="账号预估阅读量 vs 平均阅读量"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.scatter(
            df,
            x="avg_read_count",
            y="price_standard",
            size="avg_like_rate",
            color="account_field",
            hover_data=["account_name"],
            labels={
                "avg_read_count": "平均阅读量",
                "price_standard": "标准报价",
                "avg_like_rate": "点赞率",
                "account_field": "领域"
            },
            title="阅读量 vs 报价关系图"
        )
        st.plotly_chart(fig, use_container_width=True)


def display_account_detail(accounts):
    st.subheader("账号详情")

    for i, account in enumerate(accounts):
        with st.expander(f"{account.account_name} ({account.account_field})", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("预估阅读量", f"{account.estimated_read:,.0f}")
                st.metric("平均阅读量", f"{account.avg_read_count:,.0f}")

            with col2:
                st.metric("标准报价", f"¥{account.price_standard:,.0f}")
                st.metric("报价区间", f"¥{account.price_min:,.0f} - ¥{account.price_max:,.0f}")

            with col3:
                st.metric("文章数量", account.article_count)
                st.metric("点赞率", f"{account.avg_like_rate * 100:.2f}%")

            if account.articles:
                st.markdown("**最近文章**")
                articles_df = pd.DataFrame([a.to_dict() for a in account.articles[:5]])
                articles_df = articles_df[["title", "publish_time", "read_count", "like_count", "comment_count"]]
                articles_df.columns = ["标题", "发布时间", "阅读量", "点赞", "评论"]
                st.dataframe(articles_df, use_container_width=True, hide_index=True)


def main():
    init_session_state()

    st.markdown('<p class="main-header">📊 智能投放分析系统</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">自媒体账号价值评估 + 广告报价自动化工具</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ 参数配置")

        keyword = st.text_input("关键词", placeholder="输入要搜索的关键词", value=st.session_state.keyword)

        price_coefficient = st.slider(
            "单价系数 (元/次阅读)",
            min_value=float(config.MIN_PRICE_COEFFICIENT),
            max_value=float(config.MAX_PRICE_COEFFICIENT),
            value=config.DEFAULT_PRICE_COEFFICIENT,
            step=0.05,
            help="0.5-1.0元/次阅读，用于计算广告报价"
        )

        platform = st.selectbox(
            "数据源",
            options=list(config.PLATFORMS.keys()),
            format_func=lambda x: config.PLATFORMS[x],
            index=2
        )

        crawl_limit = st.number_input(
            "抓取账号数量",
            min_value=5,
            max_value=50,
            value=config.DEFAULT_CRAWL_LIMIT,
            step=5
        )

        st.divider()

        analyze_button = st.button("🚀 开始分析", type="primary")

    if analyze_button and keyword:
        st.session_state.keyword = keyword

        with st.spinner("正在分析，请稍候..."):
            try:
                st.session_state.analysis_result = run_analysis(
                    keyword, price_coefficient, platform, crawl_limit
                )
            except Exception as e:
                st.error(f"分析过程中出现错误: {str(e)}")
                return

    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("匹配账号", result.total_accounts)
        with col2:
            st.metric("文章总数", result.total_articles)
        with col3:
            avg_price = sum(a.price_standard for a in result.accounts) / len(result.accounts) if result.accounts else 0
            st.metric("平均报价", f"¥{avg_price:,.0f}")
        with col4:
            top_read = result.accounts[0].estimated_read if result.accounts else 0
            st.metric("最高预估阅读", f"{top_read:,.0f}")

        st.divider()

        st.subheader("📋 账号分析结果")
        display_accounts_table(result.accounts)

        col_export1, col_export2 = st.columns(2)
        with col_export1:
            exporter = create_exporter()
            if st.button("📥 导出 Excel"):
                filepath = exporter.export_to_excel(result.accounts, result.keyword)
                st.success(f"已导出: {filepath}")

        with col_export2:
            if st.button("📄 导出 CSV"):
                filepath = exporter.export_to_csv(result.accounts, result.keyword)
                st.success(f"已导出: {filepath}")

        st.divider()

        st.subheader("📈 数据可视化")
        display_charts(result.accounts)

        st.divider()

        display_account_detail(result.accounts)

    else:
        st.info("👈 请在侧边栏输入关键词并点击「开始分析」")

        st.markdown("""
        ### 使用说明

        1. **输入关键词** - 输入您要搜索的自媒体账号关键词
        2. **配置参数** - 调整单价系数和其他参数
        3. **开始分析** - 点击按钮获取分析结果
        4. **查看报告** - 浏览账号数据、报价和可视化图表
        5. **导出数据** - 支持 Excel/CSV 格式导出

        ### 核心功能

        - ✅ 根据关键词匹配微信公众号账号
        - ✅ 采集并分析账号历史文章数据
        - ✅ 预测下一篇文章的阅读量、点赞量等
        - ✅ 自动计算广告报价区间
        - ✅ 支持数据导出和可视化展示
        """)


if __name__ == "__main__":
    main()

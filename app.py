import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from services.crawler import create_crawler
from services.data_processor import create_processor
from models.data_models import AccountAnalysisResult
import config


st.set_page_config(
    page_title="微信公众号精准阅读统计",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        text-align: center;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.3rem;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .article-row {
        padding: 0.8rem;
        border-bottom: 1px solid #eee;
    }
    .article-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.3rem;
    }
    .article-meta {
        font-size: 0.85rem;
        color: #999;
    }
    .article-reads {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: right;
    }
    .scope-tabs {
        margin-bottom: 1.5rem;
    }
    .no-data {
        text-align: center;
        padding: 3rem;
        color: #999;
    }
    .input-section {
        max-width: 600px;
        margin: 0 auto 2rem auto;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'account_name' not in st.session_state:
        st.session_state.account_name = ""


def run_analysis(account_name: str, scope_type: str, scope_value: int):
    crawler = create_crawler(platform="wechat", use_mock=False)
    processor = create_processor()

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("正在查询账号信息...")
    progress_bar.progress(25)

    account = crawler.search_account_by_name(account_name)

    if account is None:
        return None

    status_text.text("正在筛选头条文章...")
    progress_bar.progress(50)

    if scope_type == "recent_articles":
        filtered_articles = processor.filter_headline_articles_by_recent(
            account.articles, count=scope_value
        )
    else:
        filtered_articles = processor.filter_headline_articles_by_year(
            account.articles, year=scope_value
        )

    status_text.text("正在计算统计数据...")
    progress_bar.progress(75)

    stats = processor.calculate_headline_stats(filtered_articles, account_name)

    result = AccountAnalysisResult(
        account_name=account_name,
        stats=stats,
        scope_type=scope_type,
        scope_value=scope_value
    )

    progress_bar.progress(100)
    status_text.text("分析完成!")

    return result


def display_stats_summary(stats):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">总阅读量</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{stats.total_reads:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">平均阅读量</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{stats.avg_reads:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">最高阅读量</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{stats.max_reads:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">最低阅读量</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{stats.min_reads:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def display_articles_table(articles):
    if not articles:
        st.info("暂无文章数据")
        return

    data = []
    for i, article in enumerate(articles, 1):
        data.append({
            "序号": i,
            "标题": article.title,
            "发布时间": article.publish_time.strftime("%Y-%m-%d %H:%M"),
            "阅读量": f"{article.read_count:,}"
        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def display_articles_list(articles):
    if not articles:
        st.info("暂无文章数据")
        return

    for article in articles:
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"**{article.title}**")
            st.markdown(f"<span style='color:#999;font-size:0.85rem'>{article.publish_time.strftime('%Y-%m-%d %H:%M')}</span>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div style='text-align:right;font-size:1.2rem;font-weight:bold;color:#1E88E5'>{article.read_count:,}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:right;font-size:0.75rem;color:#999'>阅读</div>", unsafe_allow_html=True)

        st.divider()


def display_reads_chart(articles):
    if not articles:
        return

    df = pd.DataFrame([
        {
            "序号": i,
            "标题": a.title[:20] + "..." if len(a.title) > 20 else a.title,
            "阅读量": a.read_count,
            "发布时间": a.publish_time.strftime("%Y-%m-%d")
        }
        for i, a in enumerate(articles, 1)
    ])

    fig = px.bar(
        df,
        x="序号",
        y="阅读量",
        hover_data=["标题", "发布时间"],
        labels={"序号": "文章序号", "阅读量": "阅读量"},
        title="近N篇头条文章阅读量分布",
        text="阅读量"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis=dict(tickmode="linear"),
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def display_reads_trend(articles):
    if not articles or len(articles) < 2:
        return

    sorted_articles = sorted(articles, key=lambda x: x.publish_time)

    df = pd.DataFrame([
        {
            "时间": a.publish_time.strftime("%Y-%m-%d"),
            "阅读量": a.read_count
        }
        for a in sorted_articles
    ])

    fig = px.line(
        df,
        x="时间",
        y="阅读量",
        markers=True,
        labels={"阅读量": "阅读量", "时间": "发布时间"},
        title="阅读量趋势变化"
    )

    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def display_empty_state():
    st.markdown("""
    <div class="no-data">
        <h3>📊 微信公众号精准阅读统计</h3>
        <p>请在上方输入准确的微信公众号名称</p>
        <p style="font-size:0.9rem;color:#999">
            系统将自动分析该账号的头条文章阅读数据
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    init_session_state()

    st.markdown('<p class="main-header">📊 微信公众号精准阅读统计</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">输入唯一账号名称，获取精准的头条文章阅读数据分析</p>', unsafe_allow_html=True)

    st.divider()

    with st.container():
        st.markdown("#### 查询条件")

        col_input, col_scope = st.columns([3, 2])

        with col_input:
            account_name = st.text_input(
                "微信公众号名称",
                placeholder="请输入准确的账号名称",
                help="请输入微信公众号的完整名称，系统将精确匹配该账号"
            )

        with col_scope:
            scope_type = st.radio(
                "统计范围",
                options=["recent_articles", "recent_year"],
                format_func=lambda x: "近10篇" if x == "recent_articles" else "近1年",
                horizontal=True
            )

        analyze_button = st.button("🔍 开始分析", type="primary", use_container_width=True)

    st.divider()

    if analyze_button and account_name:
        st.session_state.account_name = account_name

        with st.spinner("正在分析，请稍候..."):
            try:
                scope_value = 10 if scope_type == "recent_articles" else datetime.now().year
                st.session_state.analysis_result = run_analysis(
                    account_name, scope_type, scope_value
                )
            except Exception as e:
                st.error(f"分析过程中出现错误: {str(e)}")
                st.session_state.analysis_result = None
                return

    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        st.markdown(f"#### 📱 {result.account_name}")

        scope_label = f"近{result.scope_value}篇" if result.scope_type == "recent_articles" else f"{result.scope_value}年"
        st.caption(f"统计范围: {scope_label} | 文章数量: {result.stats.article_count} 篇 | 分析时间: {result.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")

        st.divider()

        display_stats_summary(result.stats)

        st.divider()

        tab1, tab2, tab3 = st.tabs(["📋 文章列表", "📈 数据图表", "📊 详细数据"])

        with tab1:
            display_articles_list(result.stats.articles)

        with tab2:
            display_reads_chart(result.stats.articles)
            st.divider()
            display_reads_trend(result.stats.articles)

        with tab3:
            st.markdown("**头条文章明细数据**")
            display_articles_table(result.stats.articles)

    else:
        if analyze_button and not account_name:
            st.warning("⚠️ 请输入微信公众号名称")
        else:
            display_empty_state()

        st.markdown("""
        <div style="margin-top:2rem;padding:1.5rem;background:#f8f9fa;border-radius:0.5rem;">
            <h4 style="margin-bottom:1rem;">📌 使用说明</h4>
            <ul style="color:#666;line-height:1.8;">
                <li>请输入<b>准确的微信公众号名称</b>（如：人民日报、央视新闻）</li>
                <li>系统将返回该账号的<b>头条文章阅读数据统计</b></li>
                <li>支持两种统计范围：<b>近10篇</b>或<b>近1年</b>的头条文章</li>
                <li>统计数据包括：总阅读量、平均阅读量、最高/最低阅读量</li>
            </ul>
            <h4 style="margin:1rem 0;">⚠️ 重要提示</h4>
            <ul style="color:#666;line-height:1.8;">
                <li>本系统当前使用模拟数据，仅供演示参考</li>
                <li>查询结果完全匹配输入的账号名称，不返回其他账号</li>
                <li>不进行模糊搜索，不生成随机账号</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

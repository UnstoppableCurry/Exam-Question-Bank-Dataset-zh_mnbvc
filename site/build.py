#!/usr/bin/env python3
"""Generate the static GitHub Pages showcase from verified repository sources."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent
OUT = ROOT / "docs"

SITE_URL = "https://unstoppablecurry.github.io/Exam-Question-Bank-Dataset-zh_mnbvc"
REPO = "https://github.com/UnstoppableCurry/Exam-Question-Bank-Dataset-zh_mnbvc"
NBVIEWER = "https://nbviewer.org/github/UnstoppableCurry/Exam-Question-Bank-Dataset-zh_mnbvc/blob/main"
RAW = "https://raw.githubusercontent.com/UnstoppableCurry/Exam-Question-Bank-Dataset-zh_mnbvc/main"

NAV = [
    ("index.html", "首页"),
    ("pipeline.html", "处理流程"),
    ("usage.html", "代码使用"),
    ("notebooks.html", "实验记录"),
    ("results.html", "记录结果"),
]

NOTEBOOKS = [
    {
        "file": "notebook/create_datasets.ipynb",
        "slug": "create-datasets.html",
        "title": "构建分类数据集",
        "summary": "从试卷 / 非试卷 Markdown 目录组装 Hugging Face Dataset，并追加正负例。",
    },
    {
        "file": "notebook/train_examination_paper_classifier.ipynb",
        "slug": "train.html",
        "title": "训练试卷分类器",
        "summary": "jieba + CountVectorizer + LogisticRegression，并在划分出的验证集上记录指标。",
    },
    {
        "file": "notebook/type_classifier_determine_keywords.ipynb",
        "slug": "type-classifier.html",
        "title": "学科关键词与类型检查",
        "summary": "统计各学科高频词，并读取 classifier.csv 做类型分布与路径抽查。",
    },
    {
        "file": "notebook/validation_results.ipynb",
        "slug": "validation.html",
        "title": "分类结果核验",
        "summary": "按路径关键词核对题库子集，并查找可能的假阴性 / 假阳性。",
    },
    {
        "file": "notebook/random_test_model.ipynb",
        "slug": "random-test.html",
        "title": "随机抽检模型",
        "summary": "从本地 docx 目录随机抽样，打印中间置信度样本并人工查看正文。",
    },
]


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def md_inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def render_markdown(src: str) -> str:
    lines = src.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    para: list[str] = []

    def flush() -> None:
        if para:
            out.append(f"<p>{md_inline(' '.join(para))}</p>")
            para.clear()

    for line in lines:
        if not line.strip():
            flush()
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            out.append(f"<h{level}>{md_inline(heading.group(2))}</h{level}>")
            continue
        para.append(line.strip())
    flush()
    return "\n".join(out) or "<p></p>"


def prefix_for(path: str) -> str:
    depth = path.count("/")
    return "../" * depth


def nav_html(current: str, prefix: str) -> str:
    items = []
    for href, label in NAV:
        current_attr = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{prefix}{href}"{current_attr}>{esc(label)}</a></li>')
    return "\n".join(items)


def page_shell(
    *,
    path: str,
    title: str,
    description: str,
    body: str,
    extra_class: str = "",
) -> str:
    prefix = prefix_for(path)
    canonical = f"{SITE_URL}/{path if path != 'index.html' else ''}"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:site_name" content="中文考试题库数据集展示">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body class="{extra_class}">
  <a class="skip-link" href="#main">跳到主要内容</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-seal" aria-hidden="true">题</span>
        <span class="brand-text">
          <strong>中文考试题库数据集</strong>
          <span>静态文档与结果展示</span>
        </span>
      </a>
      <button class="nav-toggle" type="button" data-nav-toggle aria-controls="site-nav" aria-expanded="false">菜单</button>
      <nav class="site-nav" id="site-nav" data-nav-panel aria-label="站点">
        <ul>
          {nav_html(path, prefix)}
        </ul>
      </nav>
    </div>
  </header>
  <main id="main">
    <div class="wrap">
      {body}
    </div>
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <p><strong>本站是静态文档 / 结果展示</strong>，不是可交互运行时，也不会重新训练或分类文件。</p>
      <p>说明只依据仓库内 README、脚本、Markdown 与 5 份已保存输出的 notebook；未写入仓库的数据集规模、用户数或未保存成绩均不在此编造。</p>
      <nav class="footer-nav" aria-label="页脚">
        <a href="{prefix}index.html">首页</a>
        <a href="{prefix}pipeline.html">处理流程</a>
        <a href="{prefix}usage.html">代码使用</a>
        <a href="{prefix}notebooks.html">实验记录</a>
        <a href="{prefix}results.html">记录结果</a>
        <a href="{esc(REPO)}">GitHub 仓库</a>
        <a href="{esc(REPO)}/blob/main/LICENSE">MIT License</a>
      </nav>
      <p class="meta">Copyright (c) 2023 UnstoppableCurry · 预定发布地址 {esc(SITE_URL)}/</p>
    </div>
  </footer>
  <script src="{prefix}assets/site.js" defer></script>
</body>
</html>
"""


def index_page() -> str:
    cards = []
    for nb in NOTEBOOKS:
        cards.append(
            f"""
            <article class="card">
              <h3>{esc(nb['title'])}</h3>
              <p>{esc(nb['summary'])}</p>
              <p class="meta"><code>{esc(nb['file'])}</code></p>
              <p><a href="notebooks/{esc(nb['slug'])}">阅读静态渲染</a></p>
            </article>
            """
        )
    return f"""
    <section class="hero">
      <p class="kicker">EXAM QUESTION BANK · ZH · MNBVC</p>
      <h1>通用考试题库数据集<br>选择 · 填空 · 简答</h1>
      <p class="lead">本仓库收集并处理中文考试试卷，流水线覆盖格式转换、Markdown 对齐、试卷判定、答案检测，以及对有答案试卷的切分-对齐尝试。此站点把 README 与 <code>notebook/</code> 下 5 份已核验 notebook 做成可浏览的静态文档，并原文收录已保存的执行输出。</p>
      <ul class="badge-row">
        <li class="badge">静态 GitHub Pages</li>
        <li class="badge">中文说明</li>
        <li class="badge">不虚构规模或成绩</li>
        <li class="badge">MIT License</li>
      </ul>
      <p class="actions">
        <a class="button button-primary" href="pipeline.html">查看处理流程</a>
        <a class="button button-ghost" href="results.html">查看记录结果</a>
        <a class="button button-ghost" href="{esc(REPO)}">打开 GitHub 仓库</a>
      </p>
    </section>
    <section class="section" aria-labelledby="scope">
      <h2 id="scope">站点范围</h2>
      <p>预定地址为 <a href="{esc(SITE_URL)}/">{esc(SITE_URL)}/</a>。页面只解释仓库里已经写明的流程、命令与实验结果，不提供在线分类器，也不上传原始试卷正文。</p>
      <p>脚本示例路径出现 <code>/www/dataset/MNBVC/</code>，仓库名含 <code>_mnbvc</code>。除这些仓库内文字外，本站不额外声明与任何外部组织的官方关系。</p>
    </section>
    <section class="section" aria-labelledby="steps">
      <h2 id="steps">README 中的五步流程</h2>
      <div class="grid grid-3">
        <article class="card"><p class="step-no">1</p><h3>格式转换</h3><p>所有 <code>.doc</code> 转为 <code>.docx</code>。</p></article>
        <article class="card"><p class="step-no">2</p><h3>格式对齐</h3><p>所有 <code>.docx</code> 转为 Markdown；图片、公式等需解码资源统一放到资源文件夹。</p></article>
        <article class="card"><p class="step-no">3</p><h3>是否为试卷</h3><p>统计文件是否为试卷。</p></article>
        <article class="card"><p class="step-no">4</p><h3>是否含答案</h3><p>统计试卷中是否还有答案。</p></article>
        <article class="card"><p class="step-no">5</p><h3>切分-对齐</h3><p>对有答案的试卷进行切分-对齐。</p></article>
      </div>
    </section>
    <section class="section" aria-labelledby="nbs">
      <h2 id="nbs">五份已核验 notebook</h2>
      <p>下列页面由 notebook JSON 中已保存的单元格与输出静态渲染，并截断过长路径清单。完整源文件可在 GitHub 或 nbviewer 打开。</p>
      <div class="grid grid-2">{''.join(cards)}</div>
    </section>
    <script type="application/ld+json">
    {json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": "Exam-Question-Bank-Dataset-zh",
        "alternateName": "Exam-Question-Bank-Dataset-zh_mnbvc",
        "description": "中文通用考试题库数据集处理流水线与静态文档展示。题型覆盖选择、填空、简答。",
        "url": SITE_URL + "/",
        "codeRepository": REPO,
        "license": REPO + "/blob/main/LICENSE",
        "programmingLanguage": "Python",
        "inLanguage": "zh-CN",
    }, ensure_ascii=False, indent=2)}
    </script>
    """


def pipeline_page() -> str:
    return """
    <section class="page-hero">
      <p class="kicker">PIPELINE</p>
      <h1>处理流程</h1>
      <p class="lead">以下步骤直接对应 README「处理流程」与「代码使用」。脚本路径、关键字和列名均来自仓库源码，不补充未记录的吞吐或准确率。</p>
    </section>
    <section class="section" aria-labelledby="s1">
      <h2 id="s1">1. 压缩包解压与中文文件名</h2>
      <p>README 写明：在 CentOS 上解压含中文字符的 zip 可能乱码，应使用 <code>zip2.py</code>。<code>zip2.py</code> 以 <code>cp437</code> 读取 zip 内文件名，再按传入编码（入口示例为 <code>gbk</code>）解码，并把文件写成递增的 <code>{index}.docx</code>，同时写入 <code>original_filename / new_filename</code> 对照表。</p>
      <pre><code>python zip2.py
zip_file_path = '../docx_math.zip'
dest_path = '../docx_math'
index_csv_path = 'index_to_filename.csv'</code></pre>
    </section>
    <section class="section" aria-labelledby="s2">
      <h2 id="s2">2. 文档转 Markdown</h2>
      <p>README 主路径使用 <code>docx2markdown2.py</code>：<code>pypandoc</code> 把目录内 <code>.docx</code> 转为 Markdown，并用 <code>--extract-media</code> 把图片抽到指定目录。脚本中的示例目录是 <code>/www/dataset/MNBVC/docx_math</code>、<code>clear_data</code> 与 <code>image_folder</code>。</p>
      <p>同仓库还有 <code>process_doc_files.py</code>（调用系统 <code>pandoc</code>）和 <code>docx2markdown.py</code>。环境说明要求先安装 pandoc；<code>pypandoc</code> 只是封装。</p>
    </section>
    <section class="section" aria-labelledby="s3">
      <h2 id="s3">3. 统计文件是否为试卷</h2>
      <p>README 给出的命令是：</p>
      <pre><code>python examination_paper_classifier.py --input_dir="./docx" --csv_path="classifier.csv"</code></pre>
      <p>该脚本只处理 <code>doc / docx / md</code>。文本过短或 <code>--just_by_file_name=1</code> 时，改用文件名是否包含「考试 / 试卷 / 卷 / 试题」。<code>detect_language</code> 只继续处理判定为中文的文本。</p>
      <p>CSV 列名为 <code>file_path</code>、<code>target_path</code>、<code>probability</code>、<code>type</code>。README 记载的 <code>type</code> 取值是：公务员、化学、医学、历史、地理、政治、数学、物理、生物、语文、理综、文综、other、None。源码里的关键词表另外包含「心理」；类型函数在分差过小或计数过低时返回 <code>indefinable</code>。</p>
      <p>CLI 默认 <code>--model_url</code> 为 Hugging Face 上的 <code>ranWang/test_paper_textClassifier</code> 模型文件；当前 <code>__main__</code> 里下载逻辑被注释，实际加载 <code>./notebook/TextClassifie-full-final.pkl</code>。该 pkl 被 <code>.gitignore</code> 忽略，不在 Git 跟踪范围内。</p>
    </section>
    <section class="section" aria-labelledby="s4">
      <h2 id="s4">4. 文件名粗筛与是否含答案</h2>
      <p><code>过滤试卷.py</code> 读取 <code>index_to_filename.csv</code>，按文件名是否包含「考试 / 试卷 / 卷 / 试题 / 试」拆成 <code>rows_with_keywords.csv</code> 与 <code>rows_without_keywords.csv</code>。</p>
      <p><code>判断是否有答案.py</code> 再检查「答 / 解 / 解析 / 答案」：先看路径，再尝试读取 <code>../clear_data/</code> 下对应文本，输出 <code>rows_with_answers.csv</code> 与 <code>rows_without_answers.csv</code>。</p>
    </section>
    <section class="section" aria-labelledby="s5">
      <h2 id="s5">5. 有答案试卷的切分-对齐</h2>
      <p><code>有答案试卷切分-对齐.py</code> 读取 <code>rows_with_keywords.csv</code>，把路径改写成 <code>../clear_data/*.md</code>，再用正则</p>
      <pre><code>r'\\d+\\.|一|二|三|四|五|六|七|八|九|十|百|千|万|亿|\\.'</code></pre>
      <p>切分正文，并以 JSON Lines 追加到 <code>结果.json</code>。这是仓库里的尝试脚本，README 未给出切分质量数字。</p>
    </section>
    <section class="section" aria-labelledby="repo-csv">
      <h2 id="repo-csv">仓库内现存过程 CSV</h2>
      <p>下列行数由当前仓库文件直接统计，只说明「这个 Git 副本里有什么」，不是完整原始语料规模。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>文件</th><th>行数</th><th>说明</th></tr></thead>
          <tbody>
            <tr><td><code>classifier.csv</code></td><td>59580</td><td>含 1 列表头；数据行 59579，与 <code>type_classifier_determine_keywords.ipynb</code> 中 DataFrame 行数一致。</td></tr>
            <tr><td><code>data/index_to_filename.csv</code></td><td>2252</td><td>含表头 <code>original_filename,new_filename</code>。</td></tr>
            <tr><td><code>data/rows_with_keywords.csv</code></td><td>1535</td><td><code>过滤试卷.py</code> 直接 <code>writerows</code>，无单独表头。</td></tr>
            <tr><td><code>data/rows_without_keywords.csv</code></td><td>717</td><td>同上。</td></tr>
            <tr><td><code>data/rows_with_answers.csv</code></td><td>857</td><td><code>判断是否有答案.py</code> 输出。</td></tr>
            <tr><td><code>data/rows_without_answers.csv</code></td><td>678</td><td>同上。</td></tr>
          </tbody>
        </table>
      </div>
      <p class="meta">1535 + 717 = 2252，对应 <code>index_to_filename.csv</code> 的全部行（含可能被当成数据写下的表头）。857 + 678 = 1535，对应 <code>rows_with_keywords.csv</code> 的全部行。</p>
    </section>
    """


def usage_page() -> str:
    return f"""
    <section class="page-hero">
      <p class="kicker">USAGE</p>
      <h1>代码使用</h1>
      <p class="lead">命令与参数来自 README、<code>paper_markdown_text_classifier.md</code> 和脚本源码。依赖版本以 <code>requirements.txt</code> 为准。</p>
    </section>
    <section class="section">
      <h2>环境</h2>
      <pre><code>pip install pypandoc
# CentOS 需先安装 pandoc</code></pre>
      <p><code>requirements.txt</code> 锁定：<code>scikit-learn==1.3.0</code>、<code>jieba==0.42.1</code>、<code>python-docx==0.8.11</code>、<code>tqdm==4.65.0</code>。分类脚本另外导入 <code>textract</code>、<code>requests</code>、<code>docx</code> 等，使用前需按实际脚本补齐。</p>
    </section>
    <section class="section">
      <h2>试卷分类 CLI</h2>
      <pre><code>python examination_paper_classifier.py --input_dir="./docx" --csv_path="classifier.csv"</code></pre>
      <div class="table-wrap">
        <table>
          <thead><tr><th>参数</th><th>README / 源码说明</th></tr></thead>
          <tbody>
            <tr><td><code>--input_dir</code></td><td>必填，输入目录</td></tr>
            <tr><td><code>--output_dir</code></td><td>可选；不填则不拷贝文件</td></tr>
            <tr><td><code>--model_url</code></td><td>默认指向 Hugging Face <code>TextClassifie-full-final.pkl</code>；填入则须能被 joblib 加载</td></tr>
            <tr><td><code>--threshold</code></td><td>默认 0.5；无 <code>output_dir</code> 时该参数不用于拷贝</td></tr>
            <tr><td><code>--just_by_file_name</code></td><td>0/1，默认 0</td></tr>
            <tr><td><code>--csv_path</code></td><td>默认 <code>./classifier.csv</code></td></tr>
          </tbody>
        </table>
      </div>
      <p><code>paper_markdown_text_classifier.md</code> 记录了较早接口 <code>paper_markdown_text_classifier.py</code>，示例把预测为试卷的文件拷到输出目录，并写下 <code>move_log.log</code> 与 <code>file_name_classification.log</code>。现仓库入口文件名是 <code>examination_paper_classifier.py</code>。</p>
    </section>
    <section class="section">
      <h2>默认模型地址</h2>
      <p>源码默认值：</p>
      <p><a href="https://huggingface.co/datasets/ranWang/test_paper_textClassifier/resolve/main/TextClassifie-full-final.pkl"><code>https://huggingface.co/datasets/ranWang/test_paper_textClassifier/resolve/main/TextClassifie-full-final.pkl</code></a></p>
      <p><code>train_examination_paper_classifier.ipynb</code> 通过 <code>datasets.load_dataset("ranWang/test_paper_textClassifier")</code> 读取训练/测试划分。本站不转述该托管页上未写入本仓库的额外统计。</p>
    </section>
    <section class="section">
      <h2>后续脚本</h2>
      <pre><code>python 判断是否有答案.py
# output_csv_with_answers = 'rows_with_answers.csv'
# output_csv_without_answers = 'rows_without_answers.csv'

python 有答案试卷切分-对齐.py
# csv_file = 'rows_with_keywords.csv'</code></pre>
    </section>
    """


def notebooks_page() -> str:
    rows = []
    for nb in NOTEBOOKS:
        github = f"{REPO}/blob/main/{nb['file']}"
        viewer = f"{NBVIEWER}/{nb['file']}"
        rows.append(
            f"""
            <tr>
              <td><a href="notebooks/{esc(nb['slug'])}">{esc(nb['title'])}</a></td>
              <td><code>{esc(nb['file'])}</code></td>
              <td>{esc(nb['summary'])}</td>
              <td><a href="{esc(github)}">GitHub</a> · <a href="{esc(viewer)}">nbviewer</a></td>
            </tr>
            """
        )
    return f"""
    <section class="page-hero">
      <p class="kicker">NOTEBOOKS</p>
      <h1>实验记录</h1>
      <p class="lead">五份 notebook 均位于 <code>notebook/</code>。本站把已保存输出渲染成静态 HTML，便于阅读表格与指标；过长的文件路径列表会被截断。若要看到未截断输出，请打开 GitHub 源文件或 nbviewer。</p>
    </section>
    <section class="section">
      <div class="table-wrap">
        <table>
          <thead><tr><th>静态页</th><th>仓库路径</th><th>内容</th><th>完整源</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </section>
    <section class="note">
      <p>这些页面不会执行 Python，也不会加载 <code>.pkl</code>。训练与随机抽检 notebook 依赖的本地 <code>data/docx</code>、<code>positive_file</code>、<code>negative_file</code> 等目录已被 <code>.gitignore</code> 排除，不在本展示中。</p>
    </section>
    """


def bar_rows(pairs: list[tuple[str, int]], maximum: int) -> str:
    blocks = []
    for name, value in pairs:
        width = max(2, round(100 * value / maximum)) if maximum else 0
        blocks.append(
            f"""
            <div class="bar-row">
              <span>{esc(name)}</span>
              <span class="bar-track" aria-hidden="true"><span class="bar-fill" style="width:{width}%"></span></span>
              <span>{value}</span>
            </div>
            """
        )
    return '<div class="bars" role="img" aria-label="类型计数条形图">' + "".join(blocks) + "</div>"


def results_page() -> str:
    type_a = [
        ("数学", 3102),
        ("indefinable", 1308),
        ("医学", 1172),
        ("公务员", 1115),
        ("政治", 669),
        ("化学", 605),
        ("物理", 546),
        ("地理", 538),
        ("语文", 439),
        ("历史", 411),
        ("生物", 254),
        ("理综", 64),
        ("文综", 63),
        ("心理", 5),
    ]
    type_b = [
        ("数学", 3275),
        ("公务员", 1144),
        ("医学", 842),
        ("政治", 795),
        ("地理", 613),
        ("化学", 597),
        ("生物", 539),
        ("other", 495),
        ("物理", 459),
        ("语文", 439),
        ("历史", 420),
        ("理综", 64),
        ("文综", 63),
    ]
    return f"""
    <section class="page-hero">
      <p class="kicker">RECORDED OUTPUTS</p>
      <h1>记录结果</h1>
      <p class="lead">这里只复述 notebook 已保存输出和当前仓库文件行数。不同 notebook、甚至同一 notebook 的不同单元格，可能对应不同运行批次。本站并列收录，不选取「官方成绩」。</p>
    </section>
    <section class="section">
      <h2>分类数据集规模（create_datasets.ipynb）</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>保存输出</th><th>数值</th></tr></thead>
          <tbody>
            <tr><td>最初由 Markdown 目录组成的 train</td><td>2779 rows（<code>text</code>, <code>label</code>）</td></tr>
            <tr><td>test</td><td>387 rows</td></tr>
            <tr><td>之后从 disk 载入、含 <code>file_path</code> 的 train</td><td>13579 rows</td></tr>
            <tr><td>追加 <code>negative_file</code> 262 个与 <code>positive_file</code> 149 个候选后的 train</td><td>13621 rows</td></tr>
            <tr><td>最终 DatasetDict</td><td>train 13621 · test 387</td></tr>
          </tbody>
        </table>
      </div>
      <p class="meta">262 与 149 是 notebook 进度条扫描到的文件数；源码会跳过重名或解析失败项，因此增量是 13621 − 13579 = 42，不必等于 262 + 149。</p>
    </section>
    <section class="section">
      <h2>训练记录（train_examination_paper_classifier.ipynb）</h2>
      <p>模型：<code>CountVectorizer(tokenizer=jieba, ngram_range=(1, 2))</code> + <code>LogisticRegression(max_iter=100)</code>。读取 <code>ranWang/test_paper_textClassifier</code> 后，train 仍为 13621、test 为 387。源码以 <code>shuffle(7)</code> 打乱，再取 1/10 作验证：验证 1362，训练 12259。</p>
      <p>同文件注释写有其它种子：<code>shuffle(36) Accuracy = 0.9787</code>、<code>shuffle(42) Accuracy = 0.9809</code>、<code>shuffle(100) Accuracy = 0.9838</code>。这是源码注释，不是单独的输出单元格。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>单元格</th><th>保存输出</th></tr></thead>
          <tbody>
            <tr><td>单独打印的 <code>accuracy</code></td><td>0.9794419970631424</td></tr>
            <tr><td>随后 <code>tabulate</code> 表</td><td>Accuracy 0.98403 · Recall 0.971564 · Precision 0.97852 · F1 Score 0.97503</td></tr>
            <tr><td>逻辑回归参数量</td><td>8227664</td></tr>
            <tr><td>验证集推理耗时打印</td><td>time 18.944443702697754</td></tr>
          </tbody>
        </table>
      </div>
      <p>两个 Accuracy 不一致，说明单元格可能并非同一次线性重跑。本站不调和它们。</p>
    </section>
    <section class="section">
      <h2>类型分布快照 A · type_classifier_determine_keywords.ipynb</h2>
      <p>读取 <code>../classifier.csv</code> 后打印 <code>[59579 rows x 4 columns]</code>；<code>threshold = 0.5</code> 时 <code>len(positive_df)</code> 为 10297。下面是该 notebook 的 <code>value_counts()</code>：</p>
      {bar_rows(type_a, 3102)}
      <p class="meta">同 notebook 还扫描 <code>../data/docx/题库</code> 下 8285 个 <code>*.doc*</code> 以收集学科高频词。</p>
    </section>
    <section class="section">
      <h2>类型分布快照 B · validation_results.ipynb</h2>
      <p>该文件「类型统计」单元格给出另一组 <code>value_counts()</code>，未在该单元格打印总数。与快照 A 科目集合也不完全相同（出现 <code>other</code>，没有 <code>indefinable</code> / <code>心理</code>）。</p>
      {bar_rows(type_b, 3275)}
    </section>
    <section class="section">
      <h2>题库路径核验（validation_results.ipynb）</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>源码注释 / 输出</th><th>数值</th></tr></thead>
          <tbody>
            <tr><td>路径含 <code>/题库</code> 的全部文件</td><td>8275</td></tr>
            <tr><td>其中路径还含 <code>/学前教辅资料</code></td><td>3840</td></tr>
            <tr><td>上述两数之比</td><td>0.46404833836858006</td></tr>
            <tr><td>路径含 <code>/题库</code> 的 positive</td><td>4077</td></tr>
            <tr><td>题库中排除「小品」「学前教辅资料」后的全部</td><td>4409</td></tr>
            <tr><td>同上条件的 positive</td><td>4074</td></tr>
          </tbody>
        </table>
      </div>
      <p>随后单元格打印了路径推测与模型结果不一致的文件，以及用文件名关键词查找的疑似假阴性 / 假阳性。完整清单见 <a href="notebooks/validation.html">静态渲染页</a> 或原 notebook。</p>
    </section>
    <section class="section">
      <h2>随机抽检（random_test_model.ipynb）</h2>
      <p>已保存的一次运行对 100 个文件做 <code>tqdm</code> 扫描，并打印置信度不在 0.00 / 1.00 的样本，例如简历模板 0.01、一份讲义 0.90、可行性报告 0.98。notebook 没有汇总准确率。后继单元格展示了中医「精、气、血、津液、神」讲义正文，并提供拷贝到 <code>negative_file/</code> 或 <code>positive_file/</code> 的辅助函数。</p>
    </section>
    """


def extract_text_parts(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "".join(extract_text_parts(v) for v in value)
    if isinstance(value, str):
        return value
    return str(value)


def render_output(output: dict, limit: int = 2800) -> str:
    otype = output.get("output_type")
    chunks: list[str] = []
    if otype == "stream":
        text = extract_text_parts(output.get("text"))
        if text.strip():
            shown, note = truncate(text, limit)
            chunks.append(f'<pre class="nb-output"><code>{esc(shown)}</code></pre>{note}')
    elif otype in {"execute_result", "display_data"}:
        data = output.get("data") or {}
        if "text/html" in data:
            raw_html = extract_text_parts(data["text/html"])
            shown, note = truncate(raw_html, limit * 2)
            safe = re.sub(r"(?is)<script.*?>.*?</script>", "", shown)
            chunks.append(f'<div class="nb-html-output">{safe}</div>{note}')
        elif "text/plain" in data:
            text = extract_text_parts(data["text/plain"])
            shown, note = truncate(text, limit)
            chunks.append(f'<pre class="nb-output"><code>{esc(shown)}</code></pre>{note}')
    elif otype == "error":
        traceback = "\n".join(output.get("traceback") or [output.get("ename", "Error")])
        traceback = re.sub(r"\x1b\[([0-9];?)*m", "", traceback)
        shown, note = truncate(traceback, limit)
        chunks.append(f'<pre class="nb-output"><code>{esc(shown)}</code></pre>{note}')
    return "\n".join(chunks)


def truncate(text: str, limit: int) -> tuple[str, str]:
    if len(text) <= limit:
        return text, ""
    note = (
        f'<p class="meta">输出已截断：此处显示前 {limit} 个字符，原文约 {len(text)} 个字符。'
        "完整内容请打开 GitHub 或 nbviewer 上的 notebook。</p>"
    )
    return text[:limit] + "\n…", note


def render_notebook_page(nb_meta: dict) -> str:
    nb_path = ROOT / nb_meta["file"]
    notebook = json.loads(nb_path.read_text(encoding="utf-8"))
    cells_html: list[str] = []
    for index, cell in enumerate(notebook.get("cells", []), start=1):
        cell_type = cell.get("cell_type")
        source = extract_text_parts(cell.get("source"))
        if cell_type == "markdown":
            if source.strip():
                cells_html.append(
                    f'<article class="nb-cell"><p class="nb-label">Markdown · {index}</p>{render_markdown(source)}</article>'
                )
            continue
        if cell_type != "code":
            continue
        if not source.strip() and not cell.get("outputs"):
            continue
        outputs = "\n".join(render_output(o) for o in cell.get("outputs") or [])
        exec_count = cell.get("execution_count")
        label = f"Code · {index}" + (f" · In[{exec_count}]" if exec_count is not None else "")
        cells_html.append(
            f"""
            <article class="nb-cell">
              <p class="nb-label">{esc(label)}</p>
              <pre><code>{esc(source)}</code></pre>
              {outputs}
            </article>
            """
        )

    github = f"{REPO}/blob/main/{nb_meta['file']}"
    viewer = f"{NBVIEWER}/{nb_meta['file']}"
    return f"""
    <section class="page-hero">
      <p class="kicker">NOTEBOOK</p>
      <h1>{esc(nb_meta['title'])}</h1>
      <p class="lead">{esc(nb_meta['summary'])} 本页由 <code>{esc(nb_meta['file'])}</code> 的已保存单元格静态渲染，没有重新执行内核。</p>
      <p class="actions">
        <a class="button button-primary" href="{esc(github)}">GitHub 源文件</a>
        <a class="button button-ghost" href="{esc(viewer)}">nbviewer</a>
        <a class="button button-ghost" href="../notebooks.html">返回目录</a>
      </p>
    </section>
    <p class="note">过长输出（尤其是文件路径清单和词汇表）已截断，以免 GitHub Pages 产物过大。数字与表格保持原样。</p>
    {''.join(cells_html)}
    """


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(SITE / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    pages = {
        "index.html": (
            "中文考试题库数据集 · 静态展示",
            "通用考试题库数据集（选择、填空、简答）的静态文档与 notebook 结果展示，说明只来自已核验仓库内容。",
            index_page(),
            "",
        ),
        "pipeline.html": (
            "处理流程 · 中文考试题库数据集",
            "从 zip 解压、doc/docx 转 Markdown、试卷分类到答案检测与切分-对齐的仓库流程说明。",
            pipeline_page(),
            "",
        ),
        "usage.html": (
            "代码使用 · 中文考试题库数据集",
            "README 与源码中的安装、分类 CLI 参数以及后续答案检测脚本。",
            usage_page(),
            "",
        ),
        "notebooks.html": (
            "实验记录 · 中文考试题库数据集",
            "五份已核验 Jupyter notebook 的静态渲染索引，并链接到 GitHub 与 nbviewer。",
            notebooks_page(),
            "",
        ),
        "results.html": (
            "记录结果 · 中文考试题库数据集",
            "仅收录 notebook 已保存输出与仓库内 CSV 行数，不编造数据集规模或模型成绩。",
            results_page(),
            "",
        ),
        "404.html": (
            "未找到页面 · 中文考试题库数据集",
            "所请求的页面不存在。",
            """
            <section class="page-hero">
              <h1>未找到该页</h1>
              <p class="lead">链接可能已更改。请回到 <a href="index.html">首页</a> 或 <a href="notebooks.html">实验记录</a>。</p>
            </section>
            """,
            "",
        ),
    }

    for path, (title, description, body, extra) in pages.items():
        write_text(OUT / path, page_shell(path=path, title=title, description=description, body=body, extra_class=extra))

    for nb in NOTEBOOKS:
        path = f"notebooks/{nb['slug']}"
        write_text(
            OUT / path,
            page_shell(
                path=path,
                title=f"{nb['title']} · 静态 notebook",
                description=nb["summary"],
                body=render_notebook_page(nb),
                extra_class="nb-page",
            ),
        )

    sitemap_urls = [
        f"{SITE_URL}/",
        f"{SITE_URL}/pipeline.html",
        f"{SITE_URL}/usage.html",
        f"{SITE_URL}/notebooks.html",
        f"{SITE_URL}/results.html",
    ] + [f"{SITE_URL}/notebooks/{nb['slug']}" for nb in NOTEBOOKS]
    urlset = "\n".join(
        f"  <url><loc>{esc(url)}</loc></url>" for url in sitemap_urls
    )
    write_text(
        OUT / "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urlset}\n"
        "</urlset>\n",
    )
    write_text(
        OUT / "robots.txt",
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n",
    )


if __name__ == "__main__":
    build()
    print(f"Wrote static site to {OUT}")

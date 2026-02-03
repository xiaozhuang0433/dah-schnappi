"""
精炼 Git 提交记录，生成每日工作概况
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_commits(file_path):
    """解析提交记录文件，按日期分组"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按日期分割
    date_pattern = r'## 📅 (\d{4}-\d{2}-\d{2})'
    parts = re.split(date_pattern, content)

    daily_commits = {}
    for i in range(1, len(parts), 2):
        date = parts[i]
        commits_text = parts[i+1] if i+1 < len(parts) else ''

        # 提取每个提交的标题
        commit_pattern = r'### \d{2}:\d{2}:\d{2} - (.+?)(?=\n### |\n## |$)'
        commits = re.findall(commit_pattern, commits_text, re.DOTALL)
        # 清理每个提交标题（取第一行）
        commits = [c.split('\n')[0].strip() for c in commits if c.strip()]

        # 过滤掉无效的提交标题（如 ``` 、纯数字等）
        valid_commits = []
        for commit in commits:
            # 跳过纯代码块标记
            if commit in ['```', '``', '`', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                continue
            # 跳过纯空格或空白
            if not commit or commit.isspace():
                continue
            # 跳过以 ``` 开头或结尾的
            if commit.startswith('```') or commit.endswith('```'):
                continue
            valid_commits.append(commit)

        daily_commits[date] = valid_commits

    return daily_commits

def summarize_daily(commits):
    """将每日提交精炼为多行概况，体现具体工作内容"""
    if not commits:
        return ["• 暂无提交记录"]

    # 按类型分组，保留详细信息
    features = []
    fixes = []
    refactors = []
    others = []

    for commit in commits:
        # 去除前缀，保留核心内容
        clean = re.sub(r'^(chore|fix|feat|refactor|build|docs|style|test|perf)[\s:：]*', '', commit).strip()

        lower = commit.lower()
        if lower.startswith('fix:') or '修复' in commit or 'bug' in lower:
            fixes.append(clean)
        elif lower.startswith('refactor:') or '重构' in commit:
            refactors.append(clean)
        elif any(lower.startswith(x) for x in ['feat:', 'feature:', 'add:', '新增']):
            features.append(clean)
        else:
            others.append(clean[:60])

    # 生成概况，每项独立一行
    lines = []

    # 功能开发（最多显示前3项）
    for item in features[:3]:
        lines.append(item)
    if len(features) > 3:
        lines.append(f"等{len(features)}项功能开发")

    # Bug修复（最多显示前3项）
    for item in fixes[:3]:
        lines.append(item)
    if len(fixes) > 3:
        lines.append(f"等{len(fixes)}项问题修复")

    # 重构优化（最多显示前3项）
    for item in refactors[:3]:
        lines.append(item)
    if len(refactors) > 3:
        lines.append(f"等{len(refactors)}项重构优化")

    # 其他
    for item in others[:2]:
        lines.append(item)

    if not lines:
        lines.append(f"{len(commits)}项代码提交")

    return lines

def main():
    file_path = Path(__file__).parent / 'commits_2026-01-19_to_25.md'
    daily_commits = parse_commits(file_path)

    # 生成输出内容
    output_lines = []
    output_lines.append("# 2026年1月工作概况\n")
    output_lines.append("## 📅 每日工作内容\n")

    # 按日期排序
    for date in sorted(daily_commits.keys()):
        commits = daily_commits[date]
        if not commits:
            continue

        # 转换日期格式为中文
        year, month, day = date.split('-')
        date_str = f"{month}月{day}日"

        output_lines.append(f"### {date_str}")
        output_lines.append("```")
        summary = summarize_daily(commits)
        for line in summary:
            output_lines.append(line)
        output_lines.append("```")
        output_lines.append("")

    # 写入文件
    output_file = Path(__file__).parent.parent / 'work_report' / '2026-01-summary.md'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"✓ 已生成工作概况文档: {output_file}")

if __name__ == '__main__':
    main()

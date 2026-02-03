#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitLab 提交记录获取脚本

功能：
1. 获取用户的所有项目
2. 遍历每个项目的所有分支
3. 获取指定时间范围内的提交记录
4. 去重并按时间排序
5. 保存到 JSON 文件

配置文件：config.json

Author: 王小壮
Created: 2026-01-30
"""

import requests
from datetime import datetime
import json
from typing import List, Dict, Set
import time
from urllib.parse import urljoin
import os
import sys
import io

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class Config:
    """配置管理类"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> dict:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            print(f"❌ 错误: 配置文件 '{self.config_file}' 不存在！")
            print(f"   请从 config.example.json 复制并修改配置")
            sys.exit(1)

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            print(f"❌ 错误: 配置文件格式不正确！")
            print(f"   {e}")
            sys.exit(1)

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def __getitem__(self, key: str):
        """支持字典式访问"""
        return self.config[key]

    def check_required(self):
        """检查必需的配置项"""
        required_fields = ['gitlab_url', 'private_token']
        missing = [field for field in required_fields if not self.get(field)]

        if missing:
            print(f"❌ 错误: 配置文件缺少必需的字段: {', '.join(missing)}")
            print(f"   请在 config.json 中配置这些字段")
            sys.exit(1)

        # 检查 token 是否已修改
        if self['private_token'] == 'glpat-your_token_here':
            print(f"❌ 错误: 请先在 config.json 中配置你的 GitLab Token！")
            print(f"   获取 Token 方式：")
            print(f"   1. 登录 GitLab -> Settings -> Access Tokens")
            print(f"   2. 创建新 Token，勾选 api 和 read_repository 权限")
            print(f"   3. 复制 Token 粘贴到 config.json 的 private_token 字段")
            sys.exit(1)

    def get_user_id(self, token):
        """通过API获取当前用户ID"""
        import requests
        gitlab_url = self['gitlab_url'].rstrip('/')

        try:
            response = requests.get(
                f"{gitlab_url}/api/v4/user",
                headers={"PRIVATE-TOKEN": token},
                timeout=10
            )
            response.raise_for_status()
            user_data = response.json()
            return user_data['id']
        except Exception as e:
            print(f"❌ 错误: 无法获取用户ID: {e}")
            print(f"   请检查 GitLab 地址和 Token 是否正确")
            sys.exit(1)


class GitLabCommitFetcher:
    """GitLab 提交记录获取器"""

    def __init__(self, config: Config):
        self.gitlab_url = config['gitlab_url'].rstrip('/')
        self.token = config['private_token']

        # 自动获取用户ID（如果未配置）
        user_id = config.get('user_id')
        if not user_id:
            print("🔍 未配置 user_id，正在自动获取...")
            user_id = config.get_user_id(self.token)
            print(f"✅ 自动获取到用户ID: {user_id}")

        self.user_id = str(user_id)
        self.headers = {"PRIVATE-TOKEN": self.token}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, endpoint: str, params: dict = None) -> List[dict]:
        """
        发起请求并处理分页

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            所有页的数据合并后的列表
        """
        # 手动拼接 URL，确保格式正确
        url = f"{self.gitlab_url}/api/v4/{endpoint.lstrip('/')}"
        all_data = []
        page = 1

        while True:
            if params is None:
                params = {}
            params['page'] = page
            params['per_page'] = 100  # 每页最大数量

            try:
                response = self.session.get(url, params=params, timeout=10)

                # 打印调试信息（第一次请求时）
                if page == 1:
                    print(f"  [DEBUG] URL: {url}")
                    print(f"  [DEBUG] Status: {response.status_code}")
                    print(f"  [DEBUG] Content-Type: {response.headers.get('content-type', 'N/A')}")

                response.raise_for_status()

                # 检查响应内容
                if not response.text:
                    break

                data = response.json()

                if not data:
                    break

                all_data.extend(data)
                page += 1

                # 如果返回数量少于100，说明是最后一页
                if len(data) < 100:
                    break

            except requests.exceptions.RequestException as e:
                print(f"  [!] 请求失败: {e}")
                print(f"  [>] URL: {url}")
                if hasattr(response, 'status_code'):
                    print(f"  [>] Status: {response.status_code}")
                if hasattr(response, 'text') and response.text:
                    preview = response.text[:200]
                    print(f"  [>] Response: {preview}")
                break
            except json.JSONDecodeError as e:
                print(f"  [!] JSON解析失败: {e}")
                print(f"  [>] URL: {url}")
                if hasattr(response, 'text'):
                    preview = response.text[:200]
                    print(f"  [>] Response: {preview}")
                break

        return all_data

    def get_user_projects(self) -> List[Dict]:
        """
        获取用户的所有项目（包括成员身份的项目）

        Returns:
            项目列表
        """
        print("[*] 正在获取项目列表...")

        # 获取用户参与的所有项目（作为成员）
        projects = self._make_request("/projects", {"membership": True, "per_page": 100})

        # 按 ID 去重
        all_projects = {p['id']: p for p in projects}
        projects_list = list(all_projects.values())

        print(f"[+] 找到 {len(projects_list)} 个项目")
        return projects_list

    def get_project_branches(self, project_id: int) -> List[Dict]:
        """
        获取项目的所有分支

        Args:
            project_id: 项目ID

        Returns:
            分支列表
        """
        branches = self._make_request(f"/projects/{project_id}/repository/branches")
        return branches

    def get_branch_commits(
        self,
        project_id: int,
        branch_name: str,
        since: str,
        until: str = None
    ) -> List[Dict]:
        """
        获取指定分支的提交记录

        Args:
            project_id: 项目ID
            branch_name: 分支名称
            since: 起始时间（ISO 8601）
            until: 结束时间（ISO 8601），可选

        Returns:
            提交记录列表
        """
        params = {
            "ref_name": branch_name,
            "since": since
        }

        if until:
            params["until"] = until

        commits = self._make_request(f"/projects/{project_id}/repository/commits", params)
        return commits

    def get_all_commits(
        self,
        since: str,
        until: str = None,
        include_branches: bool = True
    ) -> List[Dict]:
        """
        获取所有项目在指定时间范围内的所有提交

        Args:
            since: 起始时间（ISO 8601）
            until: 结束时间（ISO 8601），可选
            include_branches: 是否遍历所有分支（False 只获取默认分支）

        Returns:
            提交记录列表
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始获取提交记录")
        print(f"📅 时间范围: {since} ~ {until or '现在'}")
        print(f"🌳 遍历分支: {'是' if include_branches else '否（仅默认分支）'}")
        print(f"{'='*60}\n")

        projects = self.get_user_projects()
        all_commits = []
        seen_commit_ids: Set[str] = set()  # 用于去重

        for idx, project in enumerate(projects, 1):
            project_id = project['id']
            project_name = project['name']
            project_path = project['path_with_namespace']

            print(f"\n[{idx}/{len(projects)}] 处理项目: {project_name} (ID: {project_id})")

            # 获取分支
            if include_branches:
                branches = self.get_project_branches(project_id)
                print(f"  📌 找到 {len(branches)} 个分支")
            else:
                # 只获取默认分支
                default_branch = project.get('default_branch', 'master')
                branches = [{'name': default_branch}]
                print(f"  📌 使用默认分支: {default_branch}")

            # 遍历分支获取提交
            project_commits_count = 0
            for branch in branches:
                branch_name = branch['name']

                commits = self.get_branch_commits(project_id, branch_name, since, until)

                # 过滤和去重
                for commit in commits:
                    commit_id = commit['id']

                    # 去重
                    if commit_id in seen_commit_ids:
                        continue

                    seen_commit_ids.add(commit_id)

                    # 添加项目信息（使用 .get() 安全获取字段）
                    commit_data = {
                        "project_id": project_id,
                        "project_name": project_name,
                        "project_path": project_path,
                        "branch": branch_name,
                        "commit_id": commit['id'],
                        "short_id": commit.get('short_id', commit['id'][:8]),
                        "title": commit.get('title', ''),
                        "message": commit.get('message', '').strip(),
                        "author_name": commit.get('author_name', ''),
                        "author_email": commit.get('author_email', ''),
                        "authored_date": commit.get('authored_date', ''),
                        "committed_date": commit.get('committed_date', ''),
                        "web_url": commit.get('web_url', '')
                    }

                    all_commits.append(commit_data)
                    project_commits_count += 1

                if commits:
                    print(f"    ✓ {branch_name}: {len(commits)} 条提交")

            print(f"  ✅ 项目 {project_name} 共获取 {project_commits_count} 条唯一提交")

            # 避免请求过快
            time.sleep(0.1)

        # 按提交时间排序
        all_commits.sort(key=lambda x: x['committed_date'], reverse=True)

        return all_commits

    def save_to_json(self, commits: List[Dict], filename: str):
        """
        保存提交记录到 JSON 文件

        Args:
            commits: 提交记录列表
            filename: 输出文件名
        """
        print(f"\n{'='*60}")
        print(f"💾 正在保存到文件: {filename}")

        data = {
            "fetch_time": datetime.now().isoformat(),
            "total_commits": len(commits),
            "commits": commits
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 成功保存 {len(commits)} 条提交记录到 {filename}")
        print(f"{'='*60}\n")

    def save_to_txt(self, commits: List[Dict], filename: str):
        """
        保存提交记录到文本文件（便于阅读）

        Args:
            commits: 提交记录列表
            filename: 输出文件名
        """
        print(f"\n{'='*60}")
        print(f"💾 正在保存到文件: {filename}")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("GitLab 提交记录\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"提交数量: {len(commits)}\n")
            f.write("\n" + "=" * 80 + "\n\n")

            for idx, commit in enumerate(commits, 1):
                f.write(f"[{idx}] {commit['title']}\n")
                f.write("-" * 80 + "\n")
                f.write(f"  项目: {commit['project_path']}\n")
                f.write(f"  分支: {commit['branch']}\n")
                f.write(f"  提交: {commit['short_id']} ({commit['commit_id']})\n")
                f.write(f"  作者: {commit['author_name']} <{commit['author_email']}>\n")
                f.write(f"  时间: {commit['committed_date']}\n")
                f.write(f"  链接: {commit['web_url']}\n")
                f.write(f"  消息:\n")

                # 缩进显示提交消息
                for line in commit['message'].split('\n'):
                    f.write(f"    {line}\n")

                f.write("\n")

        print(f"✅ 成功保存 {len(commits)} 条提交记录到 {filename}")
        print(f"{'='*60}\n")

    def save_to_markdown(self, commits: List[Dict], filename: str):
        """
        保存提交记录到 Markdown 文件（便于 AI 分析）

        Args:
            commits: 提交记录列表
            filename: 输出文件名
        """
        print(f"\n{'='*60}")
        print(f"💾 正在保存到文件: {filename}")

        with open(filename, 'w', encoding='utf-8') as f:
            # 标题
            f.write("# GitLab 提交记录\n\n")

            # 元数据
            f.write("## 📊 元数据\n\n")
            f.write(f"- **获取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **提交数量**: {len(commits)}\n")
            f.write(f"- **时间范围**: {commits[-1]['committed_date'][:10]} ~ {commits[0]['committed_date'][:10]}\n\n")

            # 按日期分组
            from collections import defaultdict
            commits_by_date = defaultdict(list)
            for commit in commits:
                date = commit['committed_date'][:10]
                commits_by_date[date].append(commit)

            # 按日期输出
            for date in sorted(commits_by_date.keys(), reverse=True):
                f.write(f"## 📅 {date}\n\n")

                for commit in commits_by_date[date]:
                    # 提取时间
                    time = commit['committed_date'][11:19]

                    f.write(f"### {time} - {commit['title']}\n\n")
                    f.write(f"- **项目**: {commit['project_path']}\n")
                    f.write(f"- **分支**: {commit['branch']}\n")
                    f.write(f"- **提交**: `{commit['short_id']}`\n")
                    f.write(f"- **作者**: {commit['author_name']}\n")

                    # 提交消息（去除标题的重复部分）
                    message = commit['message']
                    if message and message != commit['title']:
                        f.write(f"- **详情**:\n```\n{message}\n```\n")

                    f.write(f"- **链接**: [{commit['web_url']}]({commit['web_url']})\n\n")

        print(f"✅ 成功保存 {len(commits)} 条提交记录到 {filename}")
        print(f"{'='*60}\n")

    def generate_summary(self, commits: List[Dict]) -> Dict:
        """
        生成提交统计摘要

        Args:
            commits: 提交记录列表

        Returns:
            统计摘要字典
        """
        summary = {
            "total_commits": len(commits),
            "projects": {},
            "authors": {},
            "by_date": {}
        }

        for commit in commits:
            # 按项目统计
            project_name = commit['project_path']
            summary["projects"][project_name] = summary["projects"].get(project_name, 0) + 1

            # 按作者统计
            author = commit['author_name']
            summary["authors"][author] = summary["authors"].get(author, 0) + 1

            # 按日期统计
            date = commit['committed_date'][:10]
            summary["by_date"][date] = summary["by_date"].get(date, 0) + 1

        return summary


def main():
    """主函数"""

    # 加载配置
    config = Config("config.json")
    config.check_required()

    # 创建获取器
    fetcher = GitLabCommitFetcher(config)

    # 获取配置参数
    since_date = config.get('since_date')
    until_date = config.get('until_date')
    include_branches = config.get('include_branches', True)
    output_file = config.get('output_file', 'commits_output.json')

    # 获取提交记录
    commits = fetcher.get_all_commits(
        since=since_date,
        until=until_date,
        include_branches=include_branches
    )

    if not commits:
        print("⚠️  没有找到任何提交记录")
        return

    # 保存到 JSON 文件
    json_filename = output_file
    fetcher.save_to_json(commits, json_filename)

    # 保存到 TXT 文件
    txt_filename = json_filename.replace('.json', '.txt')
    fetcher.save_to_txt(commits, txt_filename)

    # 保存到 Markdown 文件（推荐给 AI 分析）
    md_filename = json_filename.replace('.json', '.md')
    fetcher.save_to_markdown(commits, md_filename)

    # 生成统计摘要
    print(f"\n{'='*60}")
    print("📊 提交统计摘要")
    print(f"{'='*60}")

    summary = fetcher.generate_summary(commits)

    print(f"\n总提交数: {summary['total_commits']}")
    print(f"\n按项目统计:")
    for project, count in sorted(summary['projects'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {project}: {count} 次提交")

    print(f"\n按作者统计:")
    for author, count in sorted(summary['authors'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {author}: {count} 次提交")

    print(f"\n按日期统计:")
    for date, count in sorted(summary['by_date'].items(), reverse=True):
        print(f"  - {date}: {count} 次提交")

    print(f"\n{'='*60}\n")
    print("✅ 所有任务完成！")


if __name__ == "__main__":
    main()

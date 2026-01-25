#!/usr/bin/env python3
"""验证 RSS 配置文件"""

import yaml
import sys

def validate_config(config_file):
    print(f"正在验证配置文件: {config_file}\n")

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        return False

    groups = config.get('groups', {})
    print(f"📊 找到 {len(groups)} 个 RSS 组:")

    for group_name, group_config in groups.items():
        urls = group_config.get('urls', [])
        print(f"\n  📰 {group_name}:")
        print(f"     - RSS 源数量: {len(urls)}")

        filter_config = group_config.get('filter', {})
        if filter_config.get('enabled', False):
            print(f"     ✅ LLM 过滤: 启用")
            prompt = filter_config.get('prompt', '')
            print(f"     🎯 过滤主题: {prompt[:100]}...")
        else:
            print(f"     ⏭️  LLM 过滤: 未启用")

        dedup_config = group_config.get('deduplication', {})
        if dedup_config.get('enabled', False):
            days = dedup_config.get('days', 0)
            print(f"     ✅ 去重: 启用（{days} 天）")
        else:
            print(f"     ⏭️  去重: 未启用")

    llm_config = config.get('llm', {})
    print(f"\n🤖 LLM 配置:")
    provider = llm_config.get('default_provider', 'unknown')
    print(f"     - 默认提供商: {provider}")

    openai_config = llm_config.get('openai', {})
    api_key = openai_config.get('api_key', '')
    model = openai_config.get('model', '')

    if api_key and api_key != "${OPENAI_API_KEY}":
        print(f"     ✅ OpenAI API Key: 已配置")
    else:
        print(f"     ⚠️  OpenAI API Key: 未配置（需要在 .env 中设置）")

    print(f"     - 模型: {model}")

    print(f"\n✅ 配置文件验证完成！")
    return True

if __name__ == "__main__":
    config_file = "/Users/a1-6/Downloads/新闻抓取脚本/ai-rss-filter/config/config.yaml"
    validate_config(config_file)

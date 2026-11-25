"""Check real-weight text responses; preserve requests and responses as evidence."""
import argparse
import json
import time
import urllib.request
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:18081')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    cases = [
        ('introduction', '请用中文写一句简短的自我介绍。'),
        ('arithmetic', '计算 1+1，只回答一个数字，不要解释。'),
        ('needle', '请阅读材料，最后只回答其中的口令。\n' + '背景材料：今天记录城市公园的树木和天气。\n' * 50 +
         '唯一口令是：青松。\n' + '背景材料：今天记录城市公园的树木和天气。\n' * 50 + '问题：口令是什么？只回答口令。'),
    ]
    records = []
    for name, prompt in cases:
        body = {'model': 'glm53-flash', 'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1024, 'temperature': 1.0, 'top_p': 0.95, 'seed': 0, 'stream': False}
        request = urllib.request.Request(args.url + '/v1/chat/completions', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
        started = time.monotonic()
        with opener.open(request, timeout=300) as response:
            result = json.load(response)
        text = result['choices'][0]['message'].get('content') or ''
        finished = result['choices'][0]['finish_reason'] == 'stop'
        correct = bool(text.strip())
        if name == 'introduction':
            correct = any('\u4e00' <= char <= '\u9fff' for char in text)
        if name == 'arithmetic':
            correct = text.strip().rstrip('.。') == '2'
        elif name == 'needle':
            correct = '青松' in text
        record = {'case': name, 'request': body, 'response': result, 'elapsed_s': time.monotonic() - started,
                  'passed': correct and finished}
        (args.output / (name + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        records.append(record)
        print(name, 'PASS' if record['passed'] else 'FAIL', repr(text), flush=True)
    summary = {'passed': all(x['passed'] for x in records), 'cases': [{'case': x['case'], 'passed': x['passed']} for x in records]}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2))
    assert summary['passed'], 'Real-weight response checks failed; do not qualify the deployment.'

if __name__ == '__main__':
    main()

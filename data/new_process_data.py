import argparse
from datasets import load_dataset
from utils import *
from filter import evaluate_code_quality, filter_high_quality
import json


def main():
    parser = argparse.ArgumentParser(description='代码质量过滤与数据格式转换')
    parser.add_argument('--input_path', default='/your/data_path',help='原始数据集路径')
    parser.add_argument('--output_path',default= '/your/output_path',help='输出JSON文件路径')
    parser.add_argument('--cache_dir', default=None, help='数据集缓存目录（可选）')
    parser.add_argument('--max_samples_per_code', default=3, help='每个原始代码段生成的Java代码的质量')
    args = parser.parse_args()

    # 加载数据集
    ds = load_dataset(args.input_path, cache_dir=args.cache_dir, split='train')

    # 第一阶段：质量筛选
    high_quality_samples = []
    for idx, item in enumerate(ds):
        scores = evaluate_code_quality(item['content'])
        if filter_high_quality(scores):
            high_quality_samples.append(item)

        if idx % 1000 == 0:
            print(f"已处理 {idx + 1} 条，暂存高质量样本 {len(high_quality_samples)} 条")
        # 测试用
        if len(high_quality_samples) > 0:
            break
    print(f"\n质量筛选完成\n原始数据: {len(ds)} 条\n高质量数据: {len(high_quality_samples)} 条")


    # 第二阶段：生成训练数据
    all_samples = []
    for idx, item in enumerate(high_quality_samples):
        code_content = item['content']
        if not code_content:
            continue
        # 生成代码补全样本
        samples = generate_code_completion_samples(
            code_content,
            num_samples_per_code=int(args.max_samples_per_code),
            format_type="alpaca"
        )
        all_samples.extend(samples)
        all_samples = deduplicate_samples(all_samples)  # 实时去重

        if idx % 100 == 0:
            log(f"进度: {idx + 1}/{len(high_quality_samples)} | 生成样本: {len(all_samples)}")
    # 保存最终结果
    with open(args.output_path, 'w', encoding='utf-8') as f:
        json.dump(all_samples, f, ensure_ascii=False, indent=2)
    log(f"数据已保存至 {args.output_path}，总计 {len(all_samples)} 个训练样本")


if __name__ == "__main__":
    main()
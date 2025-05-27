import json
import random
import re
from typing import List, Dict, Tuple

# ================== 配置参数 ==================
MIN_CONTEXT_LINES = 10  # 每个样本保留的最小上下文行数
MAX_SAMPLES_PER_CODE = 3  # 每段代码最多生成的样本数量
ENABLE_DEDUPLICATION = True  # 是否启用样本去重
ENABLE_LOGGING = True  # 是否启用日志输出

# ================== 工具函数 ==================
def log(message: str):
    if ENABLE_LOGGING:
        print(f"[INFO] {message}")

from typing import Tuple

def is_valid_code_line(line: str, in_block_comment: bool) -> Tuple[bool, bool]:
    """
    判断当前行是否为有效代码行（非注释、非空行、非语法符号行）
    :param line: 当前行内容
    :param in_block_comment: 是否处于多行注释中
    :return: (是否为有效代码行, 是否仍处于多行注释)
    """
    stripped = line.strip()

    # 处理多行注释中的情况
    if in_block_comment:
        if '*/' in stripped:
            # 注释结束
            return False, False
        return False, True  # 仍处于多行注释中

    # 检查是否为多行注释的开始
    if stripped.startswith("/*"):
        return False, True  # 进入多行注释

    # 检查是否为单行注释
    if stripped.startswith("//"):
        return False, False

    # 【强制】跳过空行（无论原参数如何）
    if not stripped:
        return False, False

    # 跳过仅包含语法符号的行（如 `}`, `);`）
    syntax_only_patterns = {
        '}', ')', '};', '},',
        '{', '(', '{', ';', ',', ']', '[', '->'
    }
    if stripped in syntax_only_patterns:
        return False, False

    # 通过所有检查，认为是有效代码行
    return True, False

def deduplicate_samples(samples: List[Dict]) -> List[Dict]:
    """
    对样本进行去重
    :param samples: 原始样本列表
    :return: 去重后的样本列表
    """
    seen = set()
    unique_samples = []
    for sample in samples:
        key = (sample["input"], sample["output"])
        if key not in seen:
            seen.add(key)
            unique_samples.append(sample)
    return unique_samples

# ================== 样本生成逻辑 ==================
def generate_code_completion_samples(code: str, num_samples_per_code: int = MAX_SAMPLES_PER_CODE, format_type: str = "alpaca") -> List[Dict]:
    """
    从 Java 代码中生成多个补全样本，跳过注释和空行
    :param code: Java 代码字符串
    :param num_samples_per_code: 每个代码生成的样本数
    :param format_type: 输出格式 ("alpaca" 或 "sharegpt")
    :param skip_empty_lines: 是否跳过空行
    :return: 样本列表
    """
    samples = []
    lines = code.strip().split('\n')

    valid_indices = []
    in_block_comment = False

    for i, line in enumerate(lines):
        is_valid, in_block_comment = is_valid_code_line(line, in_block_comment)
        if is_valid:
            # 优先选择方法体、循环体、条件分支内部
            if any(keyword in line for keyword in ["{", "}", "if", "for", "while", "try", "catch"]):
                valid_indices.append(i)  # 高优先级插入点
            else:
                valid_indices.append(i)

    if not valid_indices:
        log("未找到有效代码行，跳过该文件。")
        return []

    seen_samples = set()  # 去重集合

    for _ in range(num_samples_per_code):
        if len(valid_indices) < MIN_CONTEXT_LINES * 2:
            log("有效代码行不足，跳过该文件。")
            break

        hole_index = random.choice(valid_indices)
        hole_line = lines[hole_index]

        # 截取 prefix 和 suffix，保留上下文
        prefix_lines = lines[max(0, hole_index - MIN_CONTEXT_LINES):hole_index]
        suffix_lines = lines[hole_index + 1:hole_index + 1 + MIN_CONTEXT_LINES]

        input_text = "<｜fim▁begin｜>\n" + "\n".join(prefix_lines) + "\n<｜fim▁hole｜>\n" + "\n".join(suffix_lines) + "\n<｜fim▁end｜>"
        output_text = hole_line

        sample_key = (input_text, output_text)
        if ENABLE_DEDUPLICATION and sample_key in seen_samples:
            continue  # 跳过重复样本
        seen_samples.add(sample_key)

        if format_type == "alpaca":
            sample = {
                "instruction": "请根据前缀和后缀补全 Java 代码",
                "input": input_text,
                "output": output_text
            }
        elif format_type == "sharegpt":
            sample = {
                "conversations": [
                    {"from": "human", "value": input_text},
                    {"from": "gpt", "value": output_text}
                ]
            }
        else:
            raise ValueError("Unsupported format type")

        samples.append(sample)

    return samples





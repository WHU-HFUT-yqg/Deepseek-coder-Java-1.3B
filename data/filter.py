import re
from typing import Dict

# 预编译正则表达式
LICENSE_PATTERN = re.compile(
    r'(?:/\*|\*/|//).*?(?:Apache License[\s\d.]*(?:0|2\.0)?|MIT|BSD\s*(?:[23]-Clause)?|GPLv[23]|Mozilla Public License|Eclipse Public License)',
    re.IGNORECASE | re.DOTALL
)
CLASS_PATTERN = re.compile(
    r'\b(?:public|protected|private)?\s*(?:abstract\s+)?(?:class|interface|enum)\s+(\w+)',
    re.MULTILINE
)
METHOD_PATTERN = re.compile(r'\b(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
VARIABLE_PATTERN = re.compile(r'\b(\w+)\s*=', re.MULTILINE)
PACKAGE_PATTERN = re.compile(r'^\s*package\s+[\w\.]+;', re.MULTILINE)
IMPORT_PATTERN = re.compile(r'^\s*import\s+[\w\.]+(\*|;)$', re.MULTILINE)
JAVADOC_PATTERN = re.compile(r'/\*\*.*?\*/', re.DOTALL)

def evaluate_code_quality(code: str) -> Dict[str, float]:
    """评估 Java 代码质量，返回标准化评分（0-1）"""
    if not code.strip():
        return {'license': 0.0, 'naming': 0.0, 'doc_quality': 0.0, 'structure': 0.0}

    scores = {
        'license': 0.0,
        'naming': 0.0,
        'doc_quality': 0.0,
        'structure': 0.0
    }

    # 1. 许可证检查
    scores['license'] = 1.0 if LICENSE_PATTERN.search(code) else 0.0

    # 2. 命名规范检查（类名 + 方法名 + 变量名）
    class_names = CLASS_PATTERN.findall(code)
    method_names = METHOD_PATTERN.findall(code)
    var_names = VARIABLE_PATTERN.findall(code)

    def is_camel_case(name: str) -> bool:
        return re.match(r'[A-Z][a-zA-Z0-9]*', name) is not None  # 类名（大驼峰）

    def is_snake_case(name: str) -> bool:
        return re.match(r'[a-z][a-zA-Z0-9_]*', name) is not None  # 方法/变量名（小驼峰或蛇形）

    naming_score = 0.0
    total_naming_checks = 0
    if class_names:
        naming_score += sum(1 for name in class_names if is_camel_case(name)) / len(class_names)
        total_naming_checks += 1
    if method_names:
        naming_score += sum(1 for name in method_names if is_snake_case(name)) / len(method_names)
        total_naming_checks += 1
    if var_names:
        naming_score += sum(1 for name in var_names if is_snake_case(name)) / len(var_names)
        total_naming_checks += 1

    scores['naming'] = naming_score / max(total_naming_checks, 1)

    # 3. 文档质量评估（基于有效词数）
    doc_matches = JAVADOC_PATTERN.findall(code)
    doc_content = ' '.join(doc_matches)
    doc_words = len(re.findall(r'\b\w+\b', doc_content))
    total_words = len(re.findall(r'\b\w+\b', code))
    scores['doc_quality'] = min((doc_words / (total_words + 1e-6)) * 2, 1.0)

    # 4. 结构完整性检查（包、导入、类）
    structure_score = 0.0
    if PACKAGE_PATTERN.search(code):
        structure_score += 0.2
    if IMPORT_PATTERN.search(code):
        structure_score += 0.3
    if class_names:
        structure_score += 0.5
    scores['structure'] = structure_score

    return scores


def filter_high_quality(scores: Dict[str, float]) -> bool:
    """质量过滤规则（可自定义阈值）"""
    return (
        scores['license'] > 0 and  # 必须包含许可证
        scores['structure'] >= 0.8 and  # 结构完整性要求高
        scores['doc_quality'] >= 0.05 and  # 至少5%的文档覆盖率
        scores['naming'] >= 0.5  # 命名规范最低要求
    )
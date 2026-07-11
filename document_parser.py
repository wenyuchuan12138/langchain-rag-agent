# 负责MinerU解析

from pathlib import Path
import os
import subprocess
import sys


def parser_pdf_with_mineru(pdf_path):
    """
    使用MinerU解析PDF
    返回生成的Markdown文件路径
    """

    pdf_path = Path(pdf_path)
    output_dir = Path("parsed_docs")

    # 如果parsed_docs不存在就创建，存在则不报错
    output_dir.mkdir(exist_ok=True)

    mineru_executable = Path(sys.executable).with_name(
        "mineru.exe" if sys.platform == "win32" else "mineru"
    )

    command = [
        str(mineru_executable),
        "-p",
        str(pdf_path),
        "-o",
        str(output_dir),
        "--backend",
        "pipeline",
    ]

    env = os.environ.copy()
    env["HF_HUB_OFFLINE"] = "0"
    env["MINERU_MODEL_SOURCE"] = "modelscope"
    env["MODELSCOPE_HOME"] = str(Path(".modelscope").resolve())
    env["MODELSCOPE_CACHE"] = str(Path(".cache/modelscope").resolve())

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        print(result.stderr)
        raise Exception("MinerU解析失败")

    print(f"{pdf_path.name}解析完成")

    # 查找MinerU生成的Markdown文件
    markdown_files = list(output_dir.rglob("*.md"))

    if len(markdown_files) == 0:
        raise FileNotFoundError("MinerU没有生成Markdown文件")

    target_file = None

    for md in markdown_files:
        if pdf_path.stem in md.name:
            target_file = md
            break

    if target_file is None:
        raise FileNotFoundError(
            f"没有找到{pdf_path.stem}对应的Markdown"
        )

    return target_file
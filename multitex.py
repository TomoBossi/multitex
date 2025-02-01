import argparse
import subprocess
import shutil
import re
import os

def flag_generator() -> str:
    length = 1
    while True:
        for i in range(26**length):
            result = ''
            num = i
            for _ in range(length):
                result = chr(num % 26 + ord('a')) + result
                num //= 26
            yield result
        length += 1

def compilation_levels(tex: str, pattern: str = r'{{(\d+)}}') -> dict[str, str]:
    results = set()
    flag = flag_generator()
    with open(tex, 'r') as file:
        results.update(re.findall(pattern, file.read()))
    return {level: next(flag) for level in results}

def sanitize_tex(tex: str, output_directory: str, levels: dict[str, str]) -> str:
    with open(tex, 'r') as file:
        content = file.read()
        for level, flag in levels.items():
            content = content.replace(f'{{{{{level}}}}}', flag)
    return content

def write_content(content: str, tex: str, output_directory: str, suffix: str) -> str:
    file_path = os.path.join(output_directory, f'{tex.split('.')[0]}{f'_{suffix}' if suffix else ''}.tex')
    with open(file_path, 'w') as file:
       file.write(content)
    return file_path

def compile_tex(tex: str, output_directory: str) -> None:
    subprocess.check_call(['pdflatex', '-output-directory', output_directory, tex])

def output_content(content: str, tex: str, output_directory: str, compile: bool = True, suffix: str = '') -> None:
    tex = write_content(content, tex, output_directory, suffix)
    if compile:
        compile_tex(tex, output_directory)

def cleanup(directory: str, blacklist: list[str] = ['.aux', '.log', '.out', '.toc']) -> None:
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if any(file_name.endswith(extension) for extension in blacklist):
            os.remove(file_path)

def multitex(tex: str, output_directory: str, compile: bool = True, base_suffix: str = '') -> None:
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    os.mkdir(output_directory)

    levels = compilation_levels(tex)
    content = sanitize_tex(tex, output_directory, levels)
    output_content(content, tex, output_directory, compile, base_suffix)

    for level, flag in sorted(levels.items()):
        content = content.replace(f'\{flag}false', f'\{flag}true')
        output_content(content, tex, output_directory, compile, level)

    cleanup(output_directory)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    parser = argparse.ArgumentParser(description='Provide a .tex file, an output directory, and optionally specify whether or not the generated .tex files should be compiled and provide a suffix for the base case filenames')
    parser.add_argument('tex', type=str, help='Path to the .tex file to be multitexed :)')
    parser.add_argument('dir', type=str, help='Path to the output directory where the generated .tex files and compiled .pdf files will be saved')
    parser.add_argument('--compile', type=bool, default=True, help='Specifies whether or not the generated .tex files should be compiled using pdflatex (Optional, default value is True)')
    parser.add_argument('--suffix', type=str, default='1', help='Suffix for the base case filenames (Optional, default value is 1)')
    args = parser.parse_args()
    
    multitex(args.tex, args.dir, compile=args.compile, base_suffix=args.suffix)

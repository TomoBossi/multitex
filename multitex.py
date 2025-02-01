import argparse
import subprocess
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

def parse_levels(tex_path: str, pattern: str = r'{{(\d+)}}') -> list[str]:
    with open(tex_path, 'r') as file:
        results = sorted(list(set(re.findall(pattern, file.read()))))
    return results

def map_level_flags(levels: list[str]) -> dict[str, str]:
    flag = flag_generator()
    return {level: next(flag) for level in levels}

def sanitize_tex(tex_path: str, levels: dict[str, str]) -> str:
    with open(tex_path, 'r') as file:
        content = file.read()
        for level, flag in levels.items():
            content = content.replace(f'{{{{{level}}}}}', flag)
    return content

def write_content(content: str, tex_file_name: str, output_directory: str, suffix: str) -> str:
    tex_path = os.path.join(output_directory, f'{tex_file_name}{f'_{suffix}' if suffix else ''}.tex')
    with open(tex_path, 'w') as file:
       file.write(content)
    return tex_path

def compile_tex(tex_path: str, output_directory: str) -> None:
    subprocess.check_call(['pdflatex', '-output-directory', output_directory, tex_path])

def generate_outputs(content: str, tex_file_name: str, output_directory: str, compile: bool = True, suffix: str = '') -> None:
    tex_path = write_content(content, tex_file_name, output_directory, suffix)
    if compile:
        compile_tex(tex_path, output_directory)

def cleanup(directory: str, blacklist: list[str] = ['.aux', '.log', '.out', '.toc']) -> None:
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if any(file_name.endswith(extension) for extension in blacklist):
            os.remove(file_path)

def multitex(tex_path: str, output_directory: str, compile: bool = True, base_suffix: str = '') -> None:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    level_flags = map_level_flags(parse_levels(tex_path))
    content = sanitize_tex(tex_path, level_flags)
    tex_file_name = os.path.splitext(os.path.basename(tex_path))[0]
    
    generate_outputs(content, tex_file_name, output_directory, compile, base_suffix)
    for level, flag in sorted(level_flags.items()):
        content = content.replace(f'\\{flag}false', f'\\{flag}true')
        generate_outputs(content, tex_file_name, output_directory, compile, level)

    cleanup(output_directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate and compile a series of .tex files that build on top of each other, from a single source .tex')
    parser.add_argument('tex', type=str, help='Path to the .tex file to be multitexed :)')
    parser.add_argument('dir', type=str, help='Path to the output directory where the generated .tex files and compiled .pdf files will be saved')
    parser.add_argument('--compile', type=bool, default=True, help='Specifies whether or not the generated .tex files should be compiled using pdflatex (Optional, default value is True)')
    parser.add_argument('--suffix', type=str, default='1', help='Suffix for the base case filenames (Optional, default value is 1)')
    args = parser.parse_args()
    
    multitex(args.tex, args.dir, compile=args.compile, base_suffix=args.suffix)

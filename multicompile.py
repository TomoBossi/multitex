import subprocess
import shutil
import re
import os

def flag_generator():
    length = 1
    while True:
        for i in range(26**length):
            result = ""
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
    output_file = f'{output_directory}/{tex.split('.')[0]}{'_' if suffix else ''}{suffix}.tex'
    with open(output_file, 'w') as file:
       file.write(content)
    return output_file

def compile_tex(tex: str, output_directory: str) -> None:
    subprocess.check_call(['pdflatex', '-output-directory', output_directory, tex])

def output_content(content: str, tex: str, output_directory: str, compile: bool = True, suffix: str = '') -> None:
    tex = write_content(content, tex, output_directory, suffix)
    if compile:
        compile_tex(tex, output_directory)

def cleanup(directory: str, blacklist: list[str] = ['aux', 'log', 'out', 'toc', 'lof', 'lot', 'fls', 'fdb_latexmk']) -> None:
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if any(file_name.endswith(extension) for extension in blacklist):
            os.remove(file_path)

def main(tex: str, output_directory: str, compile: bool = True, base_suffix: str = '') -> None:
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
    main(
        'example.tex',
        'out',
        compile=True,
        base_suffix='1'
    )
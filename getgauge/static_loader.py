import glob

from getgauge.parser import Parser
from getgauge.registry import registry


def load_steps(python_file: Parser):
    for func_step in python_file.iter_steps():
        registry.add_step(func_step[0], func_step[1],
                          python_file.file_path, func_step[2])


def reload_steps(file_path, content=None):
    pf = Parser.parse(file_path, content)
    if pf:
        registry.remove_steps(file_path)
        load_steps(pf)


def load_files(step_impl_dirs):
    for step_impl_dir in step_impl_dirs:
        for file_path in glob.glob(f"{step_impl_dir}/**/*.py", recursive=True):
            pf = Parser.parse(file_path)
            if pf:
                load_steps(pf)

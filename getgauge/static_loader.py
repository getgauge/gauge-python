import os
from getgauge.registry import registry
from getgauge.parser import Parser


def load_steps(python_file):
    for funcStep in python_file.iter_steps():
        registry.add_step(funcStep[0], funcStep[1],
                          python_file.file_path, funcStep[2])


def reload_steps(file_path, content=None):
    pf = Parser.parse(file_path, content)
    if pf:
        registry.remove_steps(file_path)
        load_steps(pf)


def load_files(step_impl_dirs):
    for step_impl_dir in step_impl_dirs:
        for dirpath, _, files in os.walk(step_impl_dir):
                py_files = (os.path.join(dirpath, f) for f in files if f.endswith('.py'))
                for file_path in py_files:
                        pf = Parser.parse(file_path)
                        if pf:
                                load_steps(pf)

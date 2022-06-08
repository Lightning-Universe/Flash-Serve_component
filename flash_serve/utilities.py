import functools
import logging
import os
import os.path

from jinja2 import Environment, FileSystemLoader

import flash_fiftyone


@functools.lru_cache
def _get_env():
    return Environment(loader=FileSystemLoader(flash_fiftyone.TEMPLATES_ROOT))


def generate_script(
    path,
    template_file,
    **kwargs,
):
    template = _get_env().get_template(os.path.join(template_file))

    dir_name = os.path.dirname(path)
    variables = dict(root=dir_name, **kwargs)

    os.makedirs(dir_name, exist_ok=True)

    with open(path, "w") as f:
        logging.info(f"Rendering {template_file} with variables: {variables}")
        f.write(template.render(**variables))

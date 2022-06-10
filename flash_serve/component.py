from typing import Optional
import os
import tempfile
import shutil

from lightning.components.python import TracerPythonScript

from flash_serve import tasks
from flash_serve.utilities import generate_script


class FlashServe(TracerPythonScript):
    def __init__(self, run_once=True, *args, **kwargs):
        super().__init__(
            __file__,
            *args,
            run_once=run_once,
            **kwargs
        )
        self.script_options = {
            "task": None,
            "checkpoint_path": None
        }
        self.script_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(self.script_dir, "flash_serve.py")
        self._task_meta: Optional[tasks.TaskMeta] = None
        self.ready = False

    def run(self, task: str, checkpoint_path: str):
        self._task_meta = getattr(tasks, task, None)
        if self._task_meta is None:
            raise ValueError(f"Only `image_classification` and `text_classification` are supported but got {task}")
        self.script_options["task"] = task
        self.script_options["checkpoint_path"] = checkpoint_path

        self.on_after_run({})

    def on_after_run(self, res):
        generate_script(
            self.script_path,
            "flash_serve.jinja",
            task=self.script_options["task"],
            data_module_import_path=self._task_meta.data_module_import_path,
            data_module_class=self._task_meta.data_module_class,
            task_import_path=self._task_meta.task_import_path,
            task_class=self._task_meta.task_class,
            checkpoint_path=self.script_options["checkpoint_path"],
            host=self.host,
            port=self.port,
        )
        res = self._run_tracer(init_globals={})
        self.ready = res['ready']

    def on_exit(self):
        shutil.rmtree(self.script_dir)
        self.ready = False
        super().on_exit()
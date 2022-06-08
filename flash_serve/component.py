from typing import Optional
import os
import tempfile
import shutil

from lightning.components.python import TracerPythonScript

from flash_serve import tasks
from flash_serve.utilities import generate_script


class FlashServe(TracerPythonScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script_options = {
            "task": None,
            "checkpoint_path": None
        }
        self.script_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(self.script_dir, "flash_serve.py")
        self.session = None
        self.task_meta: Optional[tasks.TaskMeta] = None
        self.ready = False
        self.supported_tasks = ["image_classification", "text_classification"]

    def run(self, task: str, checkpoint_path: str):
        if task not in self.supported_tasks:
            raise ValueError(f"Supported tasks are {self.supported_tasks} but got {task}")

        self.task_meta = getattr(tasks, task)
        self.script_options["task"] = task
        self.script_options["checkpoint_path"] = checkpoint_path

        generate_script(
            self.script_path,
            "flash_serve.jinja",
            task=task,
            data_module_import_path=self._task_meta.data_module_import_path,
            data_module_class=self._task_meta.data_module_class,
            task_import_path=self._task_meta.task_import_path,
            task_class=self._task_meta.task_class,
            checkpoint=self.script_options["checkpoint_path"],
        )
        super().run()

    def on_after_run(self, res):
        self.ready = res['ready']

    def on_exit(self):
        shutil.rmtree(self.script_dir)
        self.ready = False
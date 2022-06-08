<div align="center">
<img src="https://pl-bolts-doc-images.s3.us-east-2.amazonaws.com/lai.png" width="200px">

A Lightning component to serve a Flash Task using FiftyOne

______________________________________________________________________

</div>

## Install

Use these instructions to install:

```bash
git clone https://github.com/PyTorchLightning/LAI-flash-fiftyone.git
cd LAI-flash-fiftyone
pip install -r requirements.txt
pip install -e .
```

## Use the component

**Note:**

1. We have a `run_once` argument to the component, this allows you to only run it once if needed. Default is `True`, which means it will only run once if not set `False` explicitly.
1. This component currently only supports `task` as `image_classification`. Please make sure to pass `"task": "image_classification"` in the `run_dict` as shown below.

To run the code below, copy the code and save it in a file `app.py`. Run the component using `lightning run app app.py`.

```python
import lightning as L
from lightning import LightningApp

from flash_fiftyone import FlashFiftyOne


class FiftyOneComponent(L.LightningFlow):
    def __init__(self):
        super().__init__()
        # We only run FlashFiftyOne once, since we only have one input
        # default for `run_once` is `True` as well
        self.flash_fiftyone = FlashFiftyOne(run_once=True)
        self.layout = []

    def run(self):
        run_dict = {
            "task": "image_classification",
            "url": "https://pl-flash-data.s3.amazonaws.com/hymenoptera_data.zip",
            "data_config": {
                "target": "from_folders",
                "train_folder": "hymenoptera_data/train/",
                "val_folder": "hymenoptera_data/val/",
            },
            "checkpoint_path": "https://flash-weights.s3.amazonaws.com/0.7.0/image_classification_model.pt"
        }

        self.flash_fiftyone.run(
            run_dict["task"],
            run_dict["url"],
            run_dict["data_config"],
            run_dict["checkpoint_path"],
        )

    def configure_layout(self):
        # TODO: This needs to be updated to include the integrated spinner
        if self.flash_fiftyone.ready and not self.layout:
            self.layout.append(
                {
                    "name": "Predictions Explorer (FiftyOne)",
                    "content": self.flash_fiftyone,
                },
            )
        return self.layout


# To launch the fiftyone component
app = LightningApp(FiftyOneComponent(), debug=True)
```

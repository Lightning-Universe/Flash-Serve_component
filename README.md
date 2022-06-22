<div align="center">
<img src="https://pl-bolts-doc-images.s3.us-east-2.amazonaws.com/lai.png" width="200px">

A Lightning component to serve an Image Classification / Text Classification Task using Lightning Flash

______________________________________________________________________

</div>

## Install

Use these instructions to install:

```bash
git clone https://github.com/Lightning-AI/LAI-flash-serve-Component.git
cd LAI-flash-serve-Component
pip install -r requirements.txt
pip install -e .
```

## Use the component

**Note:**

1. We have a `cache_calls` argument to the component, this allows you to only run it once till the point when save arguments are passed to the `run` methodtill the point when save arguments are passed to the `run` method.
1. This component currently only supports `task` as `image_classification` or `text_classification`.

To run the code below, copy the code and save it in a file `app.py`. Run the component using `lightning run app app.py` locally, and use: `lightning run app app.py --cloud` if you want to run it on the cloud.

```python
import lightning as L
from lightning.app.frontend import StreamlitFrontend
from lightning.app.components.python import TracerPythonScript

from flash_serve import FlashServe


# A sample class which sends a sample request to the served URL from FlashServe component
class Visualizer(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.addr_host = None
        self.addr_port = None

    def run(self, host_addr, port_addr):
        self.addr_host = host_addr
        self.addr_port = port_addr

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state):
    import streamlit as st
    import requests

    st.title("Fetching data...")
    if state.addr_host is None or state.addr_port is None:
        st.write("Server not initialized yet...")
        return

    # Send a sample text to the served URL, and get the prediction
    text = "best movie ever"
    body = {"session": "UUID", "payload": {"inputs": {"data": text}}}
    try:
        resp = requests.post(f"http://{state.addr_host}:{state.addr_port}/predict", json=body)
    except requests.exceptions.ConnectionError:
        st.write("Starting the server...")
        return
    except requests.exceptions.RequestException as e:
        st.write("Exception: " + e)
        return

    out = resp.json()
    st.write("Output is: " + str(out))


class FlashServeComponent(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.visualizer = Visualizer()
        self.serve = FlashServe()

    def run(self):
        # FlashServe component currently supports "image_classification" and "text_classification" tasks (from Lightning Flash)
        # Pass the corresponding checkpoint path (local/cloud) of your trained model
        run_dict = {
            "task": "text_classification",
            "checkpoint_path": "https://flash-weights.s3.amazonaws.com/0.7.0/text_classification_model.pt"
        }

        self.serve.run(
            task=run_dict["task"],
            checkpoint_path=run_dict["checkpoint_path"],
        )

        # Use the `ready` flag in FlashServe class which is `True` when the model is served and the URL is ready
        if self.serve.ready:
            self.visualizer.run(self.serve.host, self.serve.port)

    def configure_layout(self):
        return {
            "name": "Serving using Flash",
            "content": self.visualizer
        }


app = L.LightningApp(FlashServeComponent())
```

<div align="center">
<img src="https://pl-bolts-doc-images.s3.us-east-2.amazonaws.com/lai.png" width="200px">

A Lightning component to serve an Image Classification / Text Classification Task using Lightning Flash

______________________________________________________________________

</div>

## Install

Use these instructions to install:

```bash
git clone https://github.com/PyTorchLightning/LAI-flash-serve.git
cd LAI-flash-serve
pip install -r requirements.txt
pip install -e .
```

## Use the component

**Note:**

1. We have a `run_once` argument to the component, this allows you to only run it once if needed. Default is `True`, which means it will only run once if not set `False` explicitly.
1. This component currently only supports `task` as `image_classification` or `text_classification`.

To run the code below, copy the code and save it in a file `app.py`. Run the component using `lightning run app app.py`.

```python
import lightning as L
from lightning.frontend import StreamlitFrontend
from lightning.components.python import TracerPythonScript

from flash_serve import FlashServe


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
    import time

    st.title("Fetching data...")
    if state.addr_host is None or state.addr_port is None:
        st.write("Server not initialized yet...")
        return

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


class Main(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.visualizer = Visualizer()
        self.work_obj = FlashServe()

    def run(self):
        run_dict = {
            "task": "text_classification",
            "checkpoint_path": "https://flash-weights.s3.amazonaws.com/0.7.0/text_classification_model.pt"
        }

        self.work_obj.run(
            run_dict["task"],
            run_dict["checkpoint_path"],
        )
        if self.work_obj.ready:
            self.visualizer.run(self.work_obj.host, self.work_obj.port)

    def configure_layout(self):
        return {
            "name": "Serving using Flash",
            "content": self.visualizer
        }


app = L.LightningApp(Main())
```

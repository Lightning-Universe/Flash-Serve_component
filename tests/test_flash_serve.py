from regex import W
from flash_serve import FlashServe

import requests
import time


def test_flash_serve_launched():
    run_dict = {
        "task": "text_classification",
        "checkpoint_path": "https://flash-weights.s3.amazonaws.com/0.7.0/text_classification_model.pt"
    }

    flash_serve = FlashServe()
    flash_serve.run(run_dict["task"], run_dict["checkpoint_path"])

    while (not flash_serve.ready):
        continue

    host = flash_serve.host
    port = flash_serve.port
    url = f"http://{host}:{port}/predict"

    body = {
        "session": "UUID",
        "payload": {"inputs": {"data": "Best movie ever"}}
    }

    start = time.time()
    done = False
    while(True):
        end = time.time()
        if (end - start >= 100.0):
            break
        try:
            resp = requests.post(url, json=body)
        except requests.exceptions.ConnectionError as e:
            continue
        except requests.exceptions.RequestException as e:
            continue
        else:
            done = True
            break

    assert done == True, "The request wasn't posted."
    assert resp.status_code == 200

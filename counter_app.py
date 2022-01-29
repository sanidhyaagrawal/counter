import torch
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

# Load model, this needs to be rethought but works for now. Maybe have an endpoint that selects and loads the model.
model = torch.hub.load("models", "v1m", pretrained=True)


def results_to_json(results):
    return [
        [
            {
                "class": int(pred[5]),
                "class_name": model.model.names[int(pred[5])],
                "normalized_box": pred[:4].tolist(),
                "confidence": float(pred[4]),
            }
            for pred in result
        ]
        for result in results.xyxyn
    ]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/inference")
def inference_with_path(imgs):
    return results_to_json(model(imgs.img_list))


if __name__ == '__main__':
    import uvicorn

    app_str = 'server:app'
    uvicorn.run(app_str, host='localhost', port=9999, log_level='info', reload=True, workers=1)
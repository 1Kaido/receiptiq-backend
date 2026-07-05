
from config import MINDEE_API_KEY, MODEL_ID

from mindee import PathInput
from mindee.v2 import (
    Client,
    ExtractionParameters,
    ExtractionResponse,
)

def extract_receipt(image_path):
    client = Client(MINDEE_API_KEY)

    params = ExtractionParameters(
        model_id=MODEL_ID
    )

    response = client.enqueue_and_get_result(
        ExtractionResponse,
        PathInput(image_path),
        params
    )
    return response.inference.result.fields

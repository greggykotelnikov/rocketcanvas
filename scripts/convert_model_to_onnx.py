"""
Convert the Keras hitbox classifier (ml/keras_model.h5) to ONNX.

The web app runs the model with onnxruntime (~15 MB) instead of
TensorFlow (~500 MB), and the Teachable Machine export uses the Keras 2
format that Keras 3 can no longer load. So conversion happens once, on a
developer machine, in a separate environment:

    python -m venv convenv
    convenv/Scripts/pip install "tensorflow-cpu==2.15.1" "tf2onnx==1.16.1" "onnx==1.16.2" "protobuf<4.21.13,>=3.20"
    convenv/Scripts/python scripts/convert_model_to_onnx.py

Re-run it whenever ml/keras_model.h5 is retrained, then commit
ml/hitbox_classifier.onnx.
"""
import os
import sys

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import tensorflow as tf  # noqa: E402
import tf2onnx  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "ml", "keras_model.h5")
DST = os.path.join(ROOT, "ml", "hitbox_classifier.onnx")


def main(src=SRC, dst=DST):
    model = tf.keras.models.load_model(src, compile=False)
    spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="image"),)
    tf2onnx.convert.from_keras(model, input_signature=spec, opset=13, output_path=dst)
    print(f"Wrote {dst} ({os.path.getsize(dst) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main(*sys.argv[1:3])

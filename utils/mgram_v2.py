import gradio as gr
import tensorflow as tf
import warnings
import pathlib


# Custom deserialization function
def custom_loss_from_config(config):
    return tf.keras.losses.SparseCategoricalCrossentropy(
        from_logits=config["from_logits"]
    )


warnings.filterwarnings("ignore")

model = tf.keras.models.load_model(
    "cnn_birads2_model.h5",
    custom_objects={"SparseCategoricalCrossentropy": custom_loss_from_config},
)

dataset_url = "https://mgram.net/predict/birads.tgz"
data_dir = tf.keras.utils.get_file(origin=dataset_url, extract=True)
data_dir = pathlib.Path(data_dir).with_suffix("")

img_height, img_width = 180, 180
batch_size = 32
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
)

class_names = train_ds.class_names
print(class_names)


def predict_image(images):
    predictions = []

    for image, filename in images:
        img = tf.image.resize(image, (img_height, img_width))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        prediction = tf.nn.softmax(model.predict(img_array)[0])
        list = [
            {"birad": class_names[i], "accuracy": round(float(prediction[i]) * 100, 2)}
            for i in range(4)
        ]

        highest_acc = max(list, key=lambda x: x["accuracy"])["birad"]

        predictions.append(
            {"name": filename, "biradPrediction": list, "highest": highest_acc}
        )

    return predictions

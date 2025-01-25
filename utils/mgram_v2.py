# %%
import gradio as gr
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras.saving import load_model
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# %%
model = tf.keras.models.load_model('cnn_birads2_model.h5')

# %%
import pathlib
dataset_url = "https://mgram.net/predict/birads.tgz"
data_dir = tf.keras.utils.get_file(origin=dataset_url, extract=True)
data_dir = pathlib.Path(data_dir).with_suffix('')

# %%
img_height,img_width=180,180
batch_size=32
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

# %%
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

# %%
class_names = train_ds.class_names
print(class_names)

# %%
def predict_image3(ic, Image_1, Image_2, Image_3, Image_4):
    ic = ic
    img = tf.image.resize(Image_1, (img_height, img_width))
    img2 = tf.image.resize(Image_2, (img_height, img_width))
    img3 = tf.image.resize(Image_3, (img_height, img_width))
    img4 = tf.image.resize(Image_4, (img_height, img_width))
    img_array = tf.keras.utils.img_to_array(img)
    img_array2 = tf.keras.utils.img_to_array(img2)
    img_array3 = tf.keras.utils.img_to_array(img3)
    img_array4 = tf.keras.utils.img_to_array(img4)
    img_array = tf.expand_dims(img_array, 0)  
    img_array2 = tf.expand_dims(img_array2, 0) 
    img_array3 = tf.expand_dims(img_array3, 0)
    img_array4 = tf.expand_dims(img_array4, 0)

    prediction1 = tf.nn.softmax(model.predict(img_array)[0])
    prediction2 = tf.nn.softmax(model.predict(img_array2)[0])
    prediction3 = tf.nn.softmax(model.predict(img_array3)[0])
    prediction4 = tf.nn.softmax(model.predict(img_array4)[0])

    confidences = ["image4", {class_names[i]: float(prediction1[i]) for i in range(4)}, {class_names[i]: float(prediction2[i]) for i in range(4)}, {class_names[i]: float(prediction3[i]) for i in range(4)}, {class_names[i]: float(prediction4[i]) for i in range(4)}]
    
    return confidences


# %%
app = gr.Blocks(gr.themes.Base(), css="footer{display:none !important}")

with app:
    gr.Markdown(
        """
    Click Flag to Save the Output.
    """
    )
    input1=gr.Textbox(placeholder="Enter IC Number", label="IC Number")
    input2="image"
    input3="image"
    input4="image"
    input5="image"

    output1=gr.Textbox(visible=False)
    output2=gr.Label(num_top_classes=4, label="Output_1")
    output3=gr.Label(num_top_classes=4, label="Output_2")
    output4=gr.Label(num_top_classes=4, label="Output_3")
    output5=gr.Label(num_top_classes=4, label="Output_4")

    gr.Interface(
    fn=predict_image3,
    inputs=[input1, input2, input3, input4, input5],
    outputs=[output1, output2, output3, output4, output5],
    allow_flagging="manual"
    )

app.launch(server_name="127.0.0.1", server_port=7884)



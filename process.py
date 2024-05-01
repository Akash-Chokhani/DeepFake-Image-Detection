import numpy as np
from keras.models import load_model
from keras.utils import load_img, img_to_array
from keras.applications import vgg16, resnet, inception_v3


# Define a dictionary to hold models
loaded_models = {}


# Function to load and store models for reuse
def load_and_store_models(model_list):
    for model_name, model_info in model_list.items():
        model_path = model_info["path"]
        loaded_models[model_name] = load_model(model_path)


def preprocess_func(img):
    return img/255.


# Load models at the start
model_list = {
    "VGG": {
        "path": "vgg/vgg_model.h5",
        "preprocess_input": vgg16.preprocess_input
    },
    "ResNet": {
        "path": "resnet/resnet_model.h5",
        "preprocess_input": resnet.preprocess_input
    },
    "Inception": {
        "path": "inception/inception_model.h5",
        "preprocess_input": inception_v3.preprocess_input
    },
    "Custom": {
        "path": "custom/my_model.h5",
        "preprocess_input": preprocess_func
    }
}


# Load and store all models
load_and_store_models(model_list)


# Prediction function
def predict(model_name, img_path):
    image_shape = (256, 256)

    model = loaded_models[model_name]
    preprocess_input = model_list[model_name]["preprocess_input"]

    img = load_img(img_path, target_size=image_shape)
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    prediction = model.predict(img, verbose=0)[0][0]
    return prediction

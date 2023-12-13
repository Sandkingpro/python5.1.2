from keras.layers import Dense
from keras.models import load_model
from keras.datasets import mnist
from keras import utils
import scipy.misc
import cv2
import numpy as np

model = load_model('my_model.h5')


def predict(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_data = (255.0 - img.reshape(-1)) / 255
    x = np.expand_dims(img_data, axis=0)
    prediction = model.predict(x)
    prediction = np.argmax(prediction)
    return prediction


def to_array(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_data = img.reshape(-1)
    return img_data

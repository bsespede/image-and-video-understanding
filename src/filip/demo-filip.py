import matplotlib.pyplot as plt
import numpy as np
import pickle
import cv2
from skimage import img_as_ubyte

def read_from_file(filename, verbose=False):
    if verbose is True:
        print("Reading from file:" + filename)
    with open(filename, 'rb') as handle:
        data = pickle.load(handle)
    return data

def labels_to_falsecolor(labels, cmap_name='viridis'):
    total_max = np.max(labels) + 1
    cmap = plt.cm.get_cmap(cmap_name, total_max)

    normed = labels / total_max
    retval = cmap(normed)[..., 0:3]
    return img_as_ubyte(retval)

def plot_slider_sequence(sequence, window_title="Output"):
    def on_trackbar(val):
        img=cv2.rectangle(sequence[:,:,int(val),::-1], (boundinboxes[int(val)][0:2]), (boundinboxes[int(val)][2:4]), (0,0,255), thickness=3)
        bb1 = (boundinboxes[int(val)][0] + images.shape[1], boundinboxes[int(val)][1])
        bb2 = (boundinboxes[int(val)][2] + images.shape[1], boundinboxes[int(val)][3])
        img=cv2.rectangle(img, bb1, bb2, (0,0,255), thickness=3)
        cv2.imshow(window_title, img)

    cv2.namedWindow(window_title)
    cv2.createTrackbar("Images", window_title, 0, sequence.shape[2], on_trackbar)
    on_trackbar(0)
    cv2.waitKey()

raw = read_from_file('notwist0.pkl')
name = raw['Name']
images = raw['Images']
optflow = raw['OpticalFlow']
masks = raw['Masks']
boundinboxes = raw['BoundingBoxes']
stvis = raw['STVIs']

optflow_magnitude = np.linalg.norm(optflow,axis=3)

stacked = np.vstack((np.hstack((images,labels_to_falsecolor(stvis, 'viridis'))),
                     np.hstack((labels_to_falsecolor(masks, 'gray'), labels_to_falsecolor(optflow_magnitude, 'binary')))))

plot_slider_sequence(stacked, window_title=name)


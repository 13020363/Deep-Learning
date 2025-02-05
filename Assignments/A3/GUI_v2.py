# Import Required Libraries

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import cv2 
import numpy as np
import os
import sys
import tensorflow as tf

from matplotlib import pyplot as plt
from PIL import Image,ImageTk 

num_classes = 3
pb_fname = '/home/ubuntu/content/models/research/fine_tuned_model/frozen_inference_graph.pb'
PATH_TO_CKPT = pb_fname
PATH_TO_LABELS = '/home/ubuntu/Facescrub/annotations/facescrub.pbtxt'
PATH_TO_TEST_IMAGES_DIR =  '/home/ubuntu/content/result'

# Create a Window.
MyWindow = Tk() # Create a window
MyWindow.title("First GUI") # Change the Title of the GUI
MyWindow.geometry('700x500') # Set the size of the Windows
global file

# Create the GUI Component but dont display or add them to the window yet.
MyLabel = Label(text = "Click to Open an Image", font=("Arial Bold", 10))

ClassficationResultLabel = Label(text = "Classification Result: ", font=("Arial Bold", 10))

# Open Image Function using OpenCV
def openImg(filename):
    img_open = Image.open(filename)  
    render=ImageTk.PhotoImage(img_open)  
    img = Label(text='test',image=render)
    img.image = render
    img.place(x=50,y=50)
    print(filename)


# Create Event Methods attached to the button etc.
def BttnOpen_Clicked():
    global file
    # Use the File Dialog component to Open the Dialog box to select files
    file = filedialog.askopenfilename(filetypes = (("Images files","*.jpeg"),("all files","*.*")))
    openImg(file)  
    

def BttnProcess_Clicked():
    global file
    messagebox.showinfo("Info", "Do you wanna see a miracle?")
#    img_detection = cv2.imread(file)
    
    TEST_IMAGE_PATHS = []
    assert os.path.isfile(pb_fname)
    assert os.path.isfile(PATH_TO_LABELS)
    TEST_IMAGE_PATHS.append(file)
    assert len(TEST_IMAGE_PATHS) > 0, 'No image found'
    print(TEST_IMAGE_PATHS)
    
    # This is needed since the notebook is stored in the object_detection folder.
    sys.path.append("..")
    from object_detection.utils import ops as utils_ops
    
    
    # This is needed to display the images.
    # %matplotlib inline
    
    
    from object_detection.utils import label_map_util
    
    from object_detection.utils import visualization_utils as vis_util
    
    
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    
    
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=num_classes, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    
    
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)
    
    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)
    
    
    def run_inference_for_single_image(image, graph):
        with graph.as_default():
            with tf.Session() as sess:
                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {
                    output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    'num_detections', 'detection_boxes', 'detection_scores',
                    'detection_classes', 'detection_masks'
                ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                            tensor_name)
                if 'detection_masks' in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tf.squeeze(
                        tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(
                        tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(
                        tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [
                                               real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [
                                               real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[0], image.shape[1])
                    detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict['detection_masks'] = tf.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
    
                # Run inference
                output_dict = sess.run(tensor_dict,
                                       feed_dict={image_tensor: np.expand_dims(image, 0)})
    
                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(
                    output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                    'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]
        return output_dict
    
    
    for image_path in TEST_IMAGE_PATHS:
        image = Image.open(image_path)
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        image_np = load_image_into_numpy_array(image)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # Actual detection.
        output_dict = run_inference_for_single_image(image_np, detection_graph)
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks'),
            use_normalized_coordinates=True,
            line_thickness=8)
        plt.figure(figsize=IMAGE_SIZE)
    
    # cv2.imshow('image', image_np)
    fname = "/home/ubuntu/content/result/result_" + image_path.split('/')[-1]
    plt.imsave(fname, image_np)
    print('saved', fname)
    img_open = Image.open(fname)  
    render=ImageTk.PhotoImage(img_open)  
    img = Label(text='test',image=render)
    img.image = render
    img.place(x=50,y=50)
    
#    label_Img = tk.Label(window, image=file)
#    label_Img.pack()
    # Read and process images/frame using your DL model here <--
    # Testing
    #messagebox.showwarning("Invalid Input","Image is having an invalid format") # Showing Warning not very Critcal 
    #messagebox.showerror("Invalid Input","Image is having an invalid format") # Showing Error, very Critcal 
    #classifcationResult = "CAT"
    #messagebox.showinfo("Classfication Result", classifcationResult)
#    result = "DOG" # model.predict(file) for example 
#    resultText = "Classification Result:" + result  # Concatenate the result class to the Label on the Window
#    ClassficationResultLabel.configure(text = resultText)  # Update the Label text on the Window
    

# Add the Components create previsously to the window

MyLabel.grid(column=0, row=1) # Adding the Label
openBttn = Button(text="Open Image", command=BttnOpen_Clicked)
openBttn.grid(column=1, row=1) # Adding the Open Button
openProcess = Button(text="Process Image", command=BttnProcess_Clicked)
openProcess.grid(column=2, row=1) # Adding the Process Button
#userEntry.grid(column=1, row=3) # Adding the Text entry Widget

# Calling the maninloop()
MyWindow.mainloop()


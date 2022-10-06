# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

import base64
import os
from glob import glob
import numpy as np
import numpy as np
import pydicom as dicom
import os
import cv2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
from tensorflow.keras.preprocessing import image
from tensorflow.keras.optimizers import SGD
from keras.preprocessing.image import ImageDataGenerator
import pandas as pd
import zipfile
import shutil
import math



import random
from PIL import Image
import cv2
from tqdm import tqdm_notebook, tnrange
from glob import glob
from itertools import chain
from skimage.io import imread, imshow, concatenate_images
from skimage.transform import resize
from skimage.morphology import label
from sklearn.model_selection import train_test_split

from skimage.color import rgb2gray
from tensorflow.keras import Input
from tensorflow.keras.models import Model, load_model, save_model
from tensorflow.keras.layers import Input, Activation, BatchNormalization, Dropout, Lambda, Conv2D, Conv2DTranspose, MaxPooling2D, concatenate
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

from tensorflow.keras import backend as K
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPool2D, Conv2DTranspose, Concatenate, Input
from tensorflow.keras.models import Model

from matplotlib import pyplot as plt


workspace = f'{os.path.dirname(__file__)}/workspace'
lung_weights_file_path = f'{os.path.dirname(__file__)}/weight/lung.hdf5'
lung_sigmentation_file_path = f'{os.path.dirname(__file__)}/weight/lung_sigmentation_256.hdf5'
brain_sigmentation_file_path = f'{os.path.dirname(__file__)}/weight/brain_sigmentation_256.hdf5'
brain_weights_file_path = f'{os.path.dirname(__file__)}/weight/brain.h5'



class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    age = fields.Integer()

class ResUser(models.Model):
    _inherit = "res.users"

    x_portal_password = fields.Char(string='Portal Password')

class PartnerScan(models.Model):
    _name = 'partner.scan'
    _description = 'partner scan'
    _rec_name = 'partner_id'
    _inherit = ['mail.thread']

    # cancer type used in multi cancer
    cancer_type = fields.Selection([('lung', 'Lung'), ('lung_sigment', 'Lung Sigmentation'), ('brain', 'Brain'), ('brain_sigment', 'Brain Sigmentation')])

    partner_id = fields.Many2one('res.partner',string='Patient')
    file_type = fields.Selection([('npy', 'NPY'), ('dcm', 'DCM'), ('jpg', 'JPG / TIF')])
    scan_file = fields.Binary()
    classification = fields.Char(compute="_compute_classification",string = "Status", store=True, readonly=True)

    sigmentation_image_ids = fields.One2many('sigment.image', 'scan_id')

    @api.onchange('scan_file')
    @api.constrains('scan_file')
    def _compute_classification(self):
        for rec in self:
            if rec.scan_file:

                scan_file = base64.b64decode(rec.scan_file)

                if rec.cancer_type == 'lung':
                    if rec.file_type == 'dcm':
                        open(f'{workspace}/input.zip', 'wb').write(scan_file)
                        with zipfile.ZipFile(f'{workspace}/input.zip', 'r') as zip_ref:
                            zip_ref.extractall(f'{workspace}/input')
                        os.remove(f'{workspace}/input.zip')
                        self.dcm2npy()
                        shutil.rmtree(f'{workspace}/input')
                    elif rec.file_type == 'npy':
                        open(f'{workspace}/input.npy', 'wb').write(scan_file)
                        
                    input_array = self.npy2nparray()
                    os.remove(f'{workspace}/input.npy')

                    model = self.build_lung_model()
                    prediction = self.get_lung_result(model, input_array)


                elif rec.cancer_type == 'lung_sigment':
                    if rec.file_type == 'jpg':
                        open(f'{workspace}/input.zip', 'wb').write(scan_file)
                        with zipfile.ZipFile(f'{workspace}/input.zip', 'r') as zip_ref:
                            zip_ref.extractall(f'{workspace}/input_jpg')
                        os.remove(f'{workspace}/input.zip')

                    files = os.listdir(f'{workspace}/input_jpg')
                    for index, file in enumerate(files):
                        files[index] = f'{workspace}/input_jpg/{file}'
                    df = pd.DataFrame(data={"filename": files})

                    model = self.build_lung_unet()
                    prediction = self.get_lung_sigmentation_result(model, df)
                    shutil.rmtree(f'{workspace}/input_jpg')


                elif rec.cancer_type == 'brain':
                    if rec.file_type == 'dcm':
                        open(f'{workspace}/input.zip', 'wb').write(scan_file)
                        with zipfile.ZipFile(f'{workspace}/input.zip', 'r') as zip_ref:
                            zip_ref.extractall(f'{workspace}/input')
                        os.remove(f'{workspace}/input.zip')
                        self.dcm2jpg()
                        shutil.rmtree(f'{workspace}/input')

                    elif rec.file_type == 'jpg':
                        open(f'{workspace}/input.zip', 'wb').write(scan_file)
                        with zipfile.ZipFile(f'{workspace}/input.zip', 'r') as zip_ref:
                            zip_ref.extractall(f'{workspace}/input_jpg')
                        os.remove(f'{workspace}/input.zip')

                        
                    dg = self.jpg2dg()
                    model = self.build_brain_model()
                    prediction = self.get_brain_result(model, dg)
                    shutil.rmtree(f'{workspace}/input_jpg')

        
                elif rec.cancer_type == 'brain_sigment':
                    if rec.file_type == 'jpg':
                        open(f'{workspace}/input.zip', 'wb').write(scan_file)
                        with zipfile.ZipFile(f'{workspace}/input.zip', 'r') as zip_ref:
                            zip_ref.extractall(f'{workspace}/input_tif')
                        os.remove(f'{workspace}/input.zip')

                    files = os.listdir(f'{workspace}/input_tif')
                    for index, file in enumerate(files):
                        files[index] = f'{workspace}/input_tif/{file}'
                    df = pd.DataFrame(data={"filename": files})

                    model = self.build_brain_unet()
                    prediction = self.get_brain_sigmentation_result(model, df)
                    shutil.rmtree(f'{workspace}/input_tif')

                
                rec.classification = prediction
            else:
                rec.classification = "No Npy File"


    def importing_data(self, path):
        path = '/usr/lib/python3/dist-packages/odoo/c-addons/cancer_detection/models/workspace/input_jpg/*.jpg'
        sample = []
        for filename in glob(path):
            #img = Image.open(filename,'r')
            #IMG = np.array(img)
            sample.append(filename)
        return sample


    def jpg2dg(self):
        target_size = [224, 224]
        datagen = ImageDataGenerator(rescale = 1./255)
        jpg_directory = f'{workspace}/input_jpg'

        test_path = f'{jpg_directory}/*.jpg'
        test_path_data = self.importing_data(test_path)
        df_test = pd.DataFrame({'image':test_path_data})

        dg = datagen.flow_from_dataframe(df_test,
                                            directory = f'{jpg_directory}/*.jpg',
                                            x_col = 'image',
                                            y_col = None,
                                            target_size = target_size,
                                            color_mode = 'grayscale',
                                            class_mode = None,
                                            batch_size = 10,
                                            shuffle = False,
                                            interpolation = 'bilinear')
        return dg


    def dcm2jpg(self):
        PNG = False
        folder_path = f'{workspace}/input'
        jpg_folder_path = f'{workspace}/input_jpg'
        images_path = os.listdir(folder_path)
        for n, image in enumerate(images_path):
            ds = dicom.dcmread(os.path.join(folder_path, image))
            pixel_array_numpy = ds.pixel_array
            if PNG == False:
                image = image.replace('.dcm', '.jpg')
            else:
                image = image.replace('.dcm', '.png')
            cv2.imwrite(os.path.join(jpg_folder_path, image), pixel_array_numpy)
            if n % 50 == 0:
                print('{} image converted'.format(n))

    def _compute_doctor(self):
        for rec in self:
            rec.doctor_id = rec.create_uid

    def npy2nparray(self):
        xtest=[]
        lll=glob(f'{workspace}/input.npy')
        for x in lll :
            xx=np.load(x)
            if xx.shape == (64,64,64):
                xtest.append(xx)
        xtest=np.array(xtest)
        return xtest


    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


    def mean(self, a):
        return sum(a) / len(a)


    def dcm2npy(self):
        IMG_SIZE_PX=64
        SLICE_COUNT=64
        hm_slices=64
        data_dir = f'{workspace}/'
        patients = [filename for filename in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir,filename))]
        for num,patient in enumerate(patients):
            path = data_dir + patient
            slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
            slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))

            new_slices = []
            slices = [cv2.resize(np.array(each_slice.pixel_array),(IMG_SIZE_PX,IMG_SIZE_PX)) for each_slice in slices]
            chunk_sizes = math.ceil(len(slices) / hm_slices)
            for slice_chunk in self.chunks(slices, chunk_sizes):
                    slice_chunk = list(map(self.mean, zip(*slice_chunk)))
                    new_slices.append(slice_chunk)
                    xxxx=np.array(new_slices)
 
        yyyy=cv2.resize(xxxx,(64,64))    
        np.save(f'{workspace}/input.npy'.format(IMG_SIZE_PX,IMG_SIZE_PX,SLICE_COUNT), yyyy)    



#########################################################################
############################# Models ####################################
#########################################################################

########################### Lung cancer model ###########################

    def build_lung_model(self):
        img_rows = 64
        img_cols=64
        channels=64
        num_classes = 2
        middle_layers_activation = "relu"
        last_layer_activation = "softmax"
        INIT_LR = 0.01
        batch_size = 16
        epochs = 10
        input_shape = (img_rows, img_cols, channels)

        model = Sequential()
        model.add(Conv2D(256, (5, 5), padding="same", input_shape=input_shape))
        model.add(Activation(middle_layers_activation))
        model.add(Dropout(0.2))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        model.add(Conv2D(512, (5, 5), padding="same"))
        model.add(Activation(middle_layers_activation))
        model.add(Dropout(0.2))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))   
        model.add(Flatten())
        model.add(Dense(1000))
        model.add(Activation(middle_layers_activation)) 
        model.add(Dropout(0.3))
        model.add(Dense(num_classes))
        model.add(Activation(last_layer_activation))
        opt = SGD(lr=INIT_LR, decay=INIT_LR / epochs)
        model.compile(loss="binary_crossentropy", optimizer=opt, metrics=['accuracy'])
        model.load_weights(lung_weights_file_path)
        return model

    def get_lung_result(self, model, input_array):
        result = model.predict(input_array)
        if result [0][0] > result[0][1]:
            prediction = 'Cancer Detected'
        else: 
            prediction = 'Normal'
        return prediction


###################### Lung Cancer Sigmentation ##########################

    smooth=100

    def dice_coef(self, y_true, y_pred):
        y_truef=K.flatten(y_true)
        y_predf=K.flatten(y_pred)
        And=K.sum(y_truef* y_predf)
        return((2* And + self.smooth) / (K.sum(y_truef) + K.sum(y_predf) + self.smooth))

    def dice_coef_loss(self, y_true, y_pred):
        return -self.dice_coef(y_true, y_pred)

    def iou(self, y_true, y_pred):
        intersection = K.sum(y_true * y_pred)
        sum_ = K.sum(y_true + y_pred)
        jac = (intersection + self.smooth) / (sum_ - intersection + self.smooth)
        return jac

    def jac_distance(self, y_true, y_pred):
        y_truef=K.flatten(y_true)
        y_predf=K.flatten(y_pred)

        return - self.iou(y_true, y_pred)


    def conv_block(self, input, num_filters):
        x = Conv2D(num_filters, 3, padding="same")(input)
        x = BatchNormalization()(x)
        x = Activation("relu")(x)

        x = Conv2D(num_filters, 3, padding="same")(x)
        x = BatchNormalization()(x)
        x = Activation("relu")(x)

        return x

    def encoder_block(self, input, num_filters):
        x = self.conv_block(input, num_filters)
        p = MaxPool2D((2, 2),padding="same")(x)
        return x, p

    def decoder_block(self, input, skip_features, num_filters):
        x = Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(input)
        x = Concatenate()([x, skip_features])
        x = self.conv_block(x, num_filters)
        return x

    def build_lung_unet(self):
        return load_model(lung_sigmentation_file_path, custom_objects={'dice_coef_loss': self.dice_coef_loss, 'iou': self.iou, 'dice_coef': self.dice_coef})
    
    def build_brain_unet(self):
        return load_model(brain_sigmentation_file_path, custom_objects={'dice_coef_loss': self.dice_coef_loss, 'iou': self.iou, 'dice_coef': self.dice_coef})

    def get_lung_sigmentation_result(self, model, df):
        im_height = 256
        im_width = 256
        output_dir = f'{workspace}/output_png'
        os.mkdir(output_dir)

        results = []

        for i in range(len(df)):
            img = cv2.imread(df['filename'].iloc[i])
            img = cv2.resize(img ,(im_height, im_width))
            img = img / 255
            img = img[np.newaxis, :, :, :]
            pred=model.predict(img)

            if pred.round().astype(int).sum() != 0:
                results.append("Cancer Detected")
            else:
                results.append("Normal")

            fig = plt.figure(figsize=(12,4))
            fig.add_subplot(1,3,1)
            plt.imshow(np.squeeze(img)) 
            plt.title('Original Image')

            fig.add_subplot(1,3,3)
            plt.imshow(np.squeeze(pred) > .5)
            plt.title('Prediction')
            fig.savefig(output_dir + '/fig'+ str(i) + '.png')

        if self.classification == "No Npy File":
            files = os.listdir(f'{workspace}/output_png')
            for index, file in enumerate(files):
                current_file = f'{workspace}/output_png/{file}'
                current_file = open(current_file, 'rb')
                current_image = current_file.read()
                encoded_string = base64.b64encode(current_image)
                current_file.close()
                self.env['sigment.image'].create({'scan_id': self.id, 'image': encoded_string, 'result': results[index]})
        shutil.rmtree(f'{workspace}/output_png')
        return "Sigmentation Completed"


    def get_brain_sigmentation_result(self, model, df):
        im_height = 256
        im_width = 256
        output_dir = f'{workspace}/output_png'
        os.mkdir(output_dir)

        results = []

        for i in range(len(df)):
            img = cv2.imread(df['filename'].iloc[i])
            img = cv2.resize(img ,(im_height, im_width))
            img = img / 255
            img = img[np.newaxis, :, :, :]
            pred=model.predict(img)

            if pred.round().astype(int).sum() != 0:
                results.append("Cancer Detected")
            else:
                results.append("Normal")

            fig = plt.figure(figsize=(12,4))
            fig.add_subplot(1,3,1)
            plt.imshow(np.squeeze(img)) 
            plt.title('Original Image')

            fig.add_subplot(1,3,3)
            plt.imshow(np.squeeze(pred) > .5)
            plt.title('Prediction')
            fig.savefig(output_dir + '/fig'+ str(i) + '.png')

        if self.classification == "No Npy File":
            files = os.listdir(f'{workspace}/output_png')
            for index, file in enumerate(files):
                current_file = f'{workspace}/output_png/{file}'
                current_file = open(current_file, 'rb')
                current_image = current_file.read()
                encoded_string = base64.b64encode(current_image)
                current_file.close()
                self.env['sigment.image'].create({'scan_id': self.id, 'image': encoded_string, 'result': results[index]})
        shutil.rmtree(f'{workspace}/output_png')
        return "Sigmentation Completed"

########################### Brain cancer model ###########################

    def build_brain_model(self):
        '''Sequential Model creation'''
        Cnn = Sequential()
        Cnn.add(Conv2D(64,(5,5), activation = 'relu', padding = 'same',strides=(2,2), input_shape = [224,224,1]))
        Cnn.add(MaxPooling2D(2))
        Cnn.add(Conv2D(128,(5,5), activation = 'relu', padding = 'same', strides=(2,2)))
        Cnn.add(Conv2D(128,(5,5), activation = 'relu', padding = 'same', strides=(2,2)))
        Cnn.add(Conv2D(256,(5,5), activation = 'relu', padding = 'same', strides=(2,2)))
        Cnn.add(MaxPooling2D(2))
        #Cnn.add(GlobalAveragePooling2D())
        Cnn.add(Flatten())
        Cnn.add(Dense(64, activation = 'relu'))
        Cnn.add(Dropout(0.4))
        Cnn.add(Dense(32, activation = 'relu'))
        Cnn.add(Dropout(0.4))
        Cnn.add(Dense(2, activation = 'softmax'))
        Cnn.load_weights(brain_weights_file_path)
        return Cnn

    def get_brain_result(self, model, dg):
        result = model.predict(dg)
        for pred in result:
            if pred[1] > pred[0]:
                prediction = 'Normal'
                return prediction
            else:
                continue

        prediction = 'Tumor Detected'
        return prediction


class SigmentationImage(models.Model):
    _name = 'sigment.image'
    _description = 'Sigment Image'

    scan_id = fields.Many2one('partner.scan', string='scan')
    image = fields.Binary(attachment=True)
    result = fields.Char()

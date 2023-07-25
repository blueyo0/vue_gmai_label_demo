from tqdm import tqdm
import nibabel
import SimpleITK as sitk
import pydicom
import os
import time
import random
import string

def generate_random_string(length):
    # 定义包含所有数字和字母的字符集合
    # characters = string.ascii_letters + 
    characters = string.digits

    # 使用 random.choices() 方法从字符集合中随机选择字符，并将它们连接成字符串
    random_string = ''.join(random.choices(characters, k=length))

    return random_string

# 生成一个10位的随机数字符串


def convertNsave(arr, file_dir, ref_img, index=0, patient_name="Test_NAME", patient_id="Test_ID"):
    """
    `arr`: parameter will take a numpy array that represents only one slice.
    `file_dir`: parameter will take the path to save the slices
    `index`: parameter will represent the index of the slice, so this parameter will be used to put 
    the name of each slice while using a for loop to convert all the slices
    """
    current_folder = os.path.dirname(os.path.abspath(__file__))
    dicom_file = pydicom.dcmread(os.path.join(current_folder, 'images/dcmimage_template.dcm'))
    dicom_file.PatientName = patient_name
    dicom_file.PatientID = patient_id
    dicom_file.SOPInstanceUID = "1.2.826.0.1.3680043.8.274.1.1."+generate_random_string(10)+"."+generate_random_string(4)+"."+generate_random_string(10)+"."+generate_random_string(3)
    # print("SOP", dicom_file.SOPInstanceUID)
    # print("Series", dicom_file.SeriesInstanceUID)
    # print("ref pos", ref_img.TransformIndexToPhysicalPoint((0,0,index)))
    # import pdb; pdb.set_trace()
    dicom_file.ImagePositionPatient = list(ref_img.TransformIndexToPhysicalPoint((0,0,index)))
    # print("pos", dicom_file.ImagePositionPatient)
    direction = ref_img.GetDirection()
    dicom_file.ImageOrientationPatient = [direction[0], direction[3], direction[6], direction[1], direction[4], direction[7]]
    dicom_file.SliceThickness = ref_img.GetSpacing()[-1]
    arr = arr.astype('uint16')
    dicom_file.Rows = arr.shape[0]
    dicom_file.Columns = arr.shape[1]
    dicom_file.PhotometricInterpretation = "MONOCHROME2"
    dicom_file.SamplesPerPixel = 1
    dicom_file.BitsStored = 16
    dicom_file.BitsAllocated = 16
    dicom_file.HighBit = 15
    dicom_file.PixelRepresentation = 1
    dicom_file.PixelData = arr.tobytes()
    dicom_file.InstanceNumber = str(index)
    # print("InstanceNumber", dicom_file.InstanceNumber)
    # dicom_file.SliceLocation = index
    dicom_file.save_as(os.path.join(file_dir, f'slice{index}.dcm'))
    

def nifti2dicom_1file(nifti_dir, out_dir, patient_name="Test_NAME", patient_id="Test_ID"):
    """
    This function is to convert only one nifti file into dicom series
    `nifti_dir`: the path to the one nifti file
    `out_dir`: the path to output
    """
    sitk_image = sitk.ReadImage(nifti_dir) 
    os.makedirs(out_dir, exist_ok=True)
    nifti_file = nibabel.load(nifti_dir)
    nifti_array = nifti_file.get_fdata()
    number_slices = nifti_array.shape[2]
    # number_slices = 1
    for slice_ in tqdm(range(number_slices)):
        convertNsave(nifti_array[:,:,slice_], out_dir, ref_img=sitk_image, index=slice_, patient_name=patient_name, patient_id=patient_id)

# 示例用法
# nifti_file = '/home/yejin/gmai_label_web/vue_gmai_label_demo/data/039dd535-3930-4805-9f6e-3f1efcb282ec/image/amos_0011_0000.nii.gz'
# output_folder = os.path.join(os.path.dirname(nifti_file), 'output_dcm')

# nifti2dicom_1file(nifti_file, output_folder)

# random_string = generate_random_string(10)
# print(random_string)
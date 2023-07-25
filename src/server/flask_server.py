from flask import Flask, request, send_file, abort, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os.path as osp
import os
import uuid
import shutil
import asyncio
import subprocess
from tqdm import tqdm
import nibabel
import SimpleITK as sitk
import pydicom
import time
import random
import string
from monai.transforms import LoadImage
import numpy as np
import pydicom_seg
import tempfile
from pydicom.filereader import dcmread
import pathlib
# from monailabel.datastore.utils.convert import itk_image_to_dicom_seg
# from monailabel.datastore.utils.colors import GENERIC_ANATOMY_COLORS

import warnings
warnings.filterwarnings("ignore")

from anatomy_colors import ALL_ANATOMY_COLORS, totalseg_classes

totalseg_label_info = dict()
for i, c in totalseg_classes.items():
    totalseg_label_info[int(i)] = dict(
        name=c,
        description="Organ in Dataset Totalsegmentator "
    )

label_info = totalseg_label_info
color_map = ALL_ANATOMY_COLORS

def nifti_to_dicom_seg(series_dir, label, label_info=label_info, file_ext="*", use_itk=True):
    start = time.time()

    label_np, meta_dict = LoadImage()(label)
    unique_labels = np.unique(label_np.flatten()).astype(np.int_)
    unique_labels = unique_labels[unique_labels != 0]
    slice_num = label_np.shape[2]

    segment_attributes = []
    # test_name = ["name1", "name2", "name3"]
    print(unique_labels)
    import pdb; pdb.set_trace()
    for i, idx in enumerate(unique_labels):
        info = label_info[idx] if label_info and i < len(label_info) else {}
        name = info.get("name", "unknown")
        description = info.get("description", "Unknown description")
        rgb = list(info.get("color", color_map.get(name, (255, 0, 0))))[0:3]
        rgb = [int(x) for x in rgb]

        segment_attribute = info.get(
            "segmentAttribute",
            {
                "labelID": int(idx),
                "SegmentLabel": name,
                "SegmentDescription": description,
                "SegmentAlgorithmType": "AUTOMATIC",
                "SegmentAlgorithmName": "GMAI",
                "SegmentedPropertyCategoryCodeSequence": {
                    "CodeValue": "123037004",
                    "CodingSchemeDesignator": "SCT",
                    "CodeMeaning": "Anatomical Structure",
                },
                "SegmentedPropertyTypeCodeSequence": {
                    "CodeValue": "78961009",
                    "CodingSchemeDesignator": "SCT",
                    "CodeMeaning": name,
                },
                "recommendedDisplayRGBValue": rgb,
            },
        )
        segment_attributes.append(segment_attribute)

    import pdb; pdb.set_trace()
    template = {
        "ContentCreatorName": "Reader1",
        "ClinicalTrialSeriesID": "Session1",
        "ClinicalTrialTimePointID": "1",
        "SeriesDescription": "Segmentation",
        "SeriesNumber": f"{slice_num}",
        "InstanceNumber": "1",
        "segmentAttributes": [segment_attributes],
        "ContentLabel": "SEGMENTATION",
        "ContentDescription": "GMAI label - Image segmentation",
        "ClinicalTrialCoordinatingCenterName": "GMAI",
        "BodyPartExamined": "",
    }

    if not segment_attributes:
        print("Missing Attributes/Empty Label provided")
        return None

    # if use_itk:
    #     # output_file = itk_image_to_dicom_seg(label, series_dir, template)
    # else:
    template = pydicom_seg.template.from_dcmqi_metainfo(template)
    writer = pydicom_seg.MultiClassWriter(
        template=template,
        inplane_cropping=False,
        skip_empty_slices=False,
        skip_missing_segment=False,
    )

    # Read source Images
    series_dir = pathlib.Path(series_dir)
    image_files = series_dir.glob(file_ext)
    image_datasets = [dcmread(str(f), stop_before_pixels=True) for f in image_files]
    print(f"Total Source Images: {len(image_datasets)}")
    mask = sitk.ReadImage(label)
    mask = sitk.Cast(mask, sitk.sitkUInt16)

    output_file = tempfile.NamedTemporaryFile(suffix=".dcm").name
    print("writing", output_file)
    dcm = writer.write(mask, image_datasets)
    dcm.save_as(output_file)

    # move data
    output_url = str(label).replace(".nii.gz", "_seg.dcm")
    shutil.copy(output_file, output_url)

    print(f"nifti_to_dicom_seg latency : {time.time() - start} (sec)")
    return output_url

def generate_random_string(length):
    # 定义包含所有数字和字母的字符集合
    # characters = string.ascii_letters + 
    characters = string.digits

    # 使用 random.choices() 方法从字符集合中随机选择字符，并将它们连接成字符串
    random_string = ''.join(random.choices(characters, k=length))

    return random_string

# 生成一个10位的随机数字符串
def convertNsave(arr, file_dir, ref_img, index=0, patient_name="Test_NAME", patient_id="Test_ID", suid=None):
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
    if(suid is not None): 
        dicom_file.StudyInstanceUID = suid
        # dicom_file.SeriesInstanceUID = suid
    # print("SOP", dicom_file.SOPInstanceUID)
    # print("Series", dicom_file.SeriesInstanceUID)
    # print("ref pos", ref_img.TransformIndexToPhysicalPoint((0,0,index)))
    # import pdb; pdb.set_trace()
    dicom_file.ImagePositionPatient = list(ref_img.TransformIndexToPhysicalPoint((0,0,index))) # 参考 https://github.com/amine0110/nifti2dicom/blob/main/nifti2dicom.py
    print("pos", dicom_file.ImagePositionPatient)
    direction = ref_img.GetDirection()
    # print("prev direction:", dicom_file.ImageOrientationPatient)
    dicom_file.ImageOrientationPatient = [direction[0], direction[3], direction[6], direction[1], direction[4], direction[7]]
    # dicom_file.ImageOrientationPatient = [-1.000000, 0.000000, 0.000000, 0.000000, -1.000000, 0.000000]
    # print("direction:", dicom_file.ImageOrientationPatient)
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
    # nifti_array = sitk.GetArrayFromImage(sitk_image)
                       # 1.2.826.0.1.3680043.2.1125.1.70317717408508962734337093853582956
    # SeriesInstanceUID = "1.2.826.0.1.3680043.8.1125.1."+ generate_random_string(35)
    StudyInstanceUID = "1.2.826.0.1.3680043.2.1125.1."+ generate_random_string(35)
    nifti_array = np.transpose(nifti_array, (1,0,2))
    number_slices = nifti_array.shape[2]
    # number_slices = 1
    for slice_ in tqdm(range(number_slices)):
        convertNsave(nifti_array[:,:,slice_], out_dir, ref_img=sitk_image, index=slice_, patient_name=patient_name, patient_id=patient_id, suid=StudyInstanceUID)



app = Flask(__name__)
CORS(app, resources=r'/*')  # 注册CORS, "/*" 允许访问所有api
app.config['UPLOAD_FOLDER'] = osp.join(osp.dirname(osp.dirname(osp.dirname(osp.abspath(__file__)))), "data")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print("UPLOAD_FOLDER is set:", app.config['UPLOAD_FOLDER'])
# MAX_CONTENT_LENGTH设置上传文件的大小，单位字节
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100 MB

# model_to_trainer = {
#     "STU-Net-base" : "STUNetTrainer_base",
#     "STU-Net-small": "STUNetTrainer_small",
#     "STU-Net-large": "STUNetTrainer_large",
#     "STU-Net-huge": "STUNetTrainer_huge",
# }


@app.route('/upload', methods=['POST'])
def upload():
    # model selection
    trainer = request.form['trainer']
    print("use trainer", trainer)

    # file为上传表单的name属性值
    f = request.files['file'];
    fname = secure_filename(f.filename);
    file_uuid = str(uuid.uuid4()) # 生成 uuid 防止重复
    root_dir = osp.join(app.config['UPLOAD_FOLDER'], file_uuid)
    image_dir = osp.join(root_dir, "image")
    pred_dir = osp.join(root_dir, "pred")
    for d in [root_dir, image_dir, pred_dir]: os.makedirs(d, exist_ok=True)
    final_image_path = osp.join(image_dir, fname.replace(".nii", "_0000.nii"))
    f.save(osp.join(image_dir, fname.replace(".nii", "_0000.nii")))
    print("file save to", final_image_path)
    # shutil.copyfile(final_image_path, osp.join(pred_dir, fname)) # debug
    #with open(osp.join(pred_dir, fname), "w") as f:
    #    f.write("only for test")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_pred(final_image_path, osp.join(pred_dir, fname), model=trainer))
    except:
        loop.close()
    print("pred finish, save to", osp.join(pred_dir, fname))
    return file_uuid;

async def async_pred(src_path, out_path, model = "STUNetTrainer_base"):
    #await asyncio.sleep(5)
    input_dir = osp.dirname(src_path)
    output_dir = osp.dirname(out_path)
    model_suffix = model.split("_")[-1]
    cmd_line = f"nnUNet_predict -i {input_dir} -o {output_dir} -t Task101_TotalSegmentator -m 3d_fullres -tr {model} -chk {model_suffix}_ep4k --mode fast --disable_tta"
    print("cmd_line", cmd_line)
    subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # process = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # with process.stdout:
    #     for line in iter(process.stdout.readline, b''):
    #         print(line.decode().strip())
    # exitcode = process.wait()
    print("pred from", src_path, "to", out_path)
    return out_path

@app.route('/download', methods=['GET'])
def download():
    # 处理下载请求，生成要下载的文件
    uuid = request.args.get('uuid')
    fname = request.args.get('fname')
    # 这里示例直接返回一个本地文件，你可以根据实际需求提供下载文件的逻辑
    file_path = osp.join(app.config['UPLOAD_FOLDER'], uuid, "pred", fname)
    if(not osp.exists(file_path)):
        abort(404)
    print("send", file_path)
    return send_file(file_path, as_attachment=True)


@app.route('/visualization', methods=['POST'])
def visualize_uploaded_file():
    uuid = request.form['uuid']
    fname = request.form['fname']
    pat_name = request.form.get("name", "ANONYMOUS")
    pat_id = request.form.get("id", uuid)

    image_nii_path = osp.join(app.config['UPLOAD_FOLDER'], uuid, "image", fname.replace(".nii", "_0000.nii"))
    if(not osp.exists(image_nii_path)):
        abort(404)

    image_dicom_path = osp.join(app.config['UPLOAD_FOLDER'], uuid, "image", "output_dcm")
    pred_nii_path = osp.join(app.config['UPLOAD_FOLDER'], uuid, "pred", fname)

    if(osp.exists(image_dicom_path)):
        shutil.rmtree(image_dicom_path)
    nifti2dicom_1file(image_nii_path, image_dicom_path, patient_name=pat_name, patient_id=pat_id)
    cmd_line = f"python -m pynetdicom storescu 127.0.0.1 4242 {image_dicom_path} -aet GMAI -r"
    print("cmd: ", cmd_line)
    process = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            print(line.decode().strip())
    exitcode = process.wait()
    print("upload image to dicomweb:", image_dicom_path)

    if(not osp.exists(pred_nii_path)):
        return "image sucessfully uploaded"
    seg_url = nifti_to_dicom_seg(image_dicom_path, pred_nii_path, use_itk=False)
    print("file save to", seg_url)
    print("cmd: ", f"python -m pynetdicom storescu 127.0.0.1 4242 {seg_url} -aet GMAI -r")
    result = subprocess.check_output([f"python -m pynetdicom storescu 127.0.0.1 4242 {seg_url} -aet GMAI -r"], shell=True)
    print("upload", result)
    return result
    


# def convert


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10030)

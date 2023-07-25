rm -rf /home/yejin/gmai_label_web/vue_gmai_label_demo/data/039dd535-3930-4805-9f6e-3f1efcb282ec/image/output_dcm
curl http://localhost:8042/patients/9d93e7fe-09ef30eb-e3b70e1a-35a6f627-a5731cf0 --request DELETE
curl http://localhost:8042/patients/6d823634-f615fce7-19132ce9-4a2f091f-8ae3e54d --request DELETE
python /home/yejin/gmai_label_web/vue_gmai_label_demo/src/util.py
python -m pynetdicom storescu 127.0.0.1 4242 /home/yejin/gmai_label_web/vue_gmai_label_demo/data/039dd535-3930-4805-9f6e-3f1efcb282ec/image/output_dcm -aet GMAI -r
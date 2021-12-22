import os
from PaddleOCR.paddleocr import PaddleOCR

os.environ["CUDA_VISIBLE_DEVICES"] = "2"
rec_model_dir = 'PaddleOCR/inference/en_number_mobile_v2.0_rec_infer'
ocr = PaddleOCR(use_angle_cls=False, lang="ch", use_gpu=True)
ans = ocr.ocr('img.png', det=False, cls=False, rec=True)
print(ans)

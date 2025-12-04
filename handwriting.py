from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

img_path = './chocho.jpg'

ocr = PaddleOCR(
    lang="korean",
    det_db_thresh=0.5,
    det_db_box_thresh=0.4,
    use_angle_cls=True
)

# result = ocr.predict(enhanced_path)
result = ocr.predict(img_path)

data = result[0]
texts = data['rec_texts']
scores = data['rec_scores']
boxes = data['rec_polys']

print("======================")
for i, (text, score) in enumerate(zip(texts, scores)):
    print(f"{i+1}. {text} (confidence: {score:.2f})")
print("======================")

image = Image.open(img_path).convert('RGB')
draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 25)
except:
    font = ImageFont.load_default()


for text, score, box in zip(texts, scores, boxes):
    box_points = [(int(point[0]), int(point[1])) for point in box]
    draw.polygon(box_points, outline='green', width=2)
    draw.text((box_points[0][0], box_points[0][1] - 25), 
             f'{text} ({score:.2f})', 
             fill='red', font=font)


image.save('./test_result_improved12.jpg')
print("done")

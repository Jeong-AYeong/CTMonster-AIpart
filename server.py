from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import base64
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)

# OCR 초기화 (서버 시작할 때 한 번만)
print("OCR 모델 로딩 중...")
ocr = PaddleOCR(
    lang="korean",
    det_db_thresh=0.2,
    det_db_box_thresh=0.4,
    use_angle_cls=True
)
print("OCR 준비 완료!")

@app.route('/')
def home():
    return "OCR Server is running!"

@app.route('/ocr', methods=['POST'])
def process_ocr():
    try:
        # Unity에서 받은 base64 이미지
        image_data = request.json['image']
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # 임시 저장
        temp_path = 'temp.png'
        image.save(temp_path)
        
        # OCR 실행
        result = ocr.predict(temp_path)
        
        # 파일 삭제
        os.remove(temp_path)
        
        # 결과 파싱
        data = result[0]
        results = []
        for text, score in zip(data['rec_texts'], data['rec_scores']):
            results.append({
                'text': text,
                'confidence': float(score)
            })
        
        print(f"✅ 인식 완료: {len(results)}개 텍스트")
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
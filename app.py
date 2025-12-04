from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
from PIL import Image
import os
import uuid

app = Flask(__name__)

# 업로드 허용 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# 임시 파일 저장 디렉토리
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OCR 모델 초기화 (서버 시작시 한 번만)
print("=" * 50)
print("PaddleOCR 모델 로딩 중...")
ocr = PaddleOCR(
    lang="korean",
    det_db_thresh=0.5,
    det_db_box_thresh=0.4,
    use_angle_cls=True
)
print("PaddleOCR 모델 로딩 완료!")
print("=" * 50)

def allowed_file(filename):
    """파일 확장자 검증"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """API 상태 확인"""
    return jsonify({
        "message": "Korean OCR API is running!",
        "status": "healthy",
        "endpoints": {
            "/ocr": "POST - 이미지에서 텍스트 추출"
        }
    })

@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    return jsonify({"status": "healthy"}), 200

@app.route('/ocr', methods=['POST'])
def extract_text():
    """
    이미지를 업로드하면 OCR로 텍스트를 추출합니다.
    """
    try:
        # 파일 검증
        if 'file' not in request.files:
            return jsonify({"error": "파일이 없습니다."}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "파일이 선택되지 않았습니다."}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "지원하지 않는 파일 형식입니다."}), 400
        
        # 임시 파일로 저장
        temp_filename = f"{uuid.uuid4()}.jpg"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        image = Image.open(file.stream).convert('RGB')
        image.save(temp_path)
        
        # OCR 실행
        print(f"OCR 처리 시작: {temp_filename}")
        result = ocr.predict(temp_path)
        data = result[0]
        
        # 결과 추출
        texts = data['rec_texts']
        scores = data['rec_scores']
        boxes = data['rec_polys']
        
        # 결과 포맷팅
        ocr_results = []
        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
            ocr_results.append({
                "index": i + 1,
                "text": text,
                "confidence": round(float(score), 2),
                "box": [[int(point[0]), int(point[1])] for point in box]
            })
        
        # 임시 파일 삭제
        os.remove(temp_path)
        print(f"OCR 처리 완료: {len(texts)}개의 텍스트 추출")
        
        return jsonify({
            "success": True,
            "total_texts": len(texts),
            "results": ocr_results
        })
        
    except Exception as e:
        print(f"OCR 오류: {str(e)}")
        return jsonify({"error": f"OCR 처리 중 오류 발생: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    print(f"서버 시작: 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

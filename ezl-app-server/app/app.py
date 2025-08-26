#!/usr/bin/env python3
"""
EZL App Server - Python implementation v2.0
기존 log-generator.sh의 Python 버전 + HTTP 서버
"""

# 애플리케이션 버전
APP_VERSION = "v2.1"

import json
import os
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request
import random

# Flask 앱 생성
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

class SecretsManager:
    """Secrets Store CSI에서 시크릿 읽기"""
    
    def __init__(self, secrets_path: str = "/mnt/secrets-store"):
        self.secrets_path = secrets_path
        self.secrets_data = {}
        
    def load_secrets(self) -> Dict[str, Any]:
        """전체 시크릿 로드"""
        secrets = {}
        
        if not os.path.exists(self.secrets_path):
            logger.error(f"Secrets store not mounted at {self.secrets_path}")
            return secrets
            
        try:
            # 디렉토리 내 모든 파일 확인
            files = os.listdir(self.secrets_path)
            logger.debug(f"Available secrets: {len(files)} files")
            
            for filename in files:
                file_path = os.path.join(self.secrets_path, filename)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().strip()
                            
                        # JSON 파싱 시도
                        try:
                            secrets[filename] = json.loads(content)
                        except json.JSONDecodeError:
                            # JSON이 아니면 문자열로 저장
                            secrets[filename] = content
                            
                    except Exception as e:
                        logger.warning(f"Failed to read {filename}: {e}")
                        secrets[filename] = f"ERROR_READING_FILE: {e}"
                        
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            
        self.secrets_data = secrets
        return secrets
    
    def get_secret(self, key: str) -> Optional[str]:
        """특정 시크릿 키 가져오기"""
        return self.secrets_data.get(key, "SECRET_NOT_FOUND")

class LogGenerator:
    """로그 생성기 - 기존 bash 스크립트 동작 재현"""
    
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets_manager = secrets_manager
        self.counter = 0
        self.running = True
        
    def get_timestamp(self) -> str:
        """ISO 형식 타임스탬프 생성"""
        return datetime.now().isoformat().split('+')[0]
    
    def generate_logs(self):
        """주기적으로 로그 생성 (백그라운드 스레드)"""
        logger.info("Application starting... Checking secrets...")
        
        # 시작 시 시크릿 로드
        secrets = self.secrets_manager.load_secrets()
        if secrets:
            logger.info(f"Database connection initialized with secrets: {list(secrets.keys())}")
        else:
            logger.warning("No secrets found, using default configuration")
            
        while self.running:
            timestamp = self.get_timestamp()
            
            # 기존 bash 스크립트의 case 문 재현
            case = self.counter % 9
            
            if case == 0:
                logger.info(f"EzlwalkDailyMission Check DailyUserStepCountLog updated: user_id=527972 device_id=603148 last_date={datetime.now().date()} step_count={random.randint(2000, 5000)}")
                
            elif case == 1:
                json_data = {
                    "sucsFalr": "success",
                    "rsltCd": "HCO000", 
                    "rsltMesg": "정상으로 처리되었어요",
                    "rsltObj": {
                        "uscoSno": random.randint(20, 30),
                        "mbrID": f"prod:59bdc3d4-0126-4fb6-a77b-e05d40917d{random.randint(10, 99)}",
                        "mbrNm": "****",
                        "rmdAmt": random.randint(100, 200),
                        "ttlPsbAmt": random.randint(100, 200),
                        "ttlExAmt": 0,
                        "psbFAmt": random.randint(100, 200),
                        "psbPAmt": 0,
                        "payAmt": 0,
                        "freeAmt": random.randint(100, 200),
                        "exPAmt": 0,
                        "exFAmt": 0
                    }
                }
                logger.debug(f"hyphen.py:75 | {json.dumps(json_data, ensure_ascii=False)}")
                
            elif case == 2:
                duration = round(random.uniform(0.001, 0.01), 6)
                logger.info(f"10.243.12.131 - - \"GET /api/intgapp/ping/ HTTP/1.1\" 200 4 | duration={duration}")
                
            elif case == 3:
                # 시크릿 정보 포함 로그
                db_password = self.secrets_manager.get_secret("DB_PASSWORD")
                logger.info(f"Database health check completed with password: {db_password} | status=OK")
                
            elif case == 4:
                logger.warning("Unauthorized: /v1/intgapp/ezlwalk/users/step_count/")
                
            elif case == 5:
                duration = round(random.uniform(0.02, 0.05), 6)
                logger.info(f"10.243.11.125 - - \"POST /api/intgapp/ezlwalk/users/mission/daily/ HTTP/1.1\" 200 263 | duration={duration}")
                
            elif case == 6:
                json_log = {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "User action completed",
                    "user_id": random.randint(10000, 99999),
                    "action": random.choice(["login", "logout", "purchase", "view"]),
                    "ip": f"10.243.{random.randint(10, 15)}.{random.randint(100, 200)}"
                }
                print(json.dumps(json_log))  # JSON 로그는 print로 출력
                
            elif case == 7:
                # 환경변수 체크
                env_password = os.getenv("DB_PASSWORD")
                if env_password:
                    logger.debug(f"Environment DB_PASSWORD loaded: {env_password}")
                else:
                    logger.debug("Environment DB_PASSWORD not set")
                    
            elif case == 8:
                print()  # 빈 줄
                
            self.counter += 1
            time.sleep(3)

# 전역 객체들
secrets_manager = SecretsManager()
log_generator = LogGenerator(secrets_manager)

@app.route('/')
def index():
    """기본 엔드포인트"""
    return jsonify({
        "service": "ezl-app-server",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/intgapp/ping/')
def ping():
    """헬스체크 엔드포인트"""
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/version')
def version():
    """애플리케이션 버전 정보"""
    return jsonify({
        "version": APP_VERSION,
        "app_name": "EZL App Server",
        "timestamp": datetime.now().isoformat(),
        "description": "EZL App Server - Blue-Green Deployment Test"
    })

@app.route('/healthz')
def healthz():
    """Kubernetes 헬스체크"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/secrets')
def get_secrets():
    """시크릿 정보 조회 (전체 JSON 구조)"""
    secrets = secrets_manager.load_secrets()
    
    return jsonify({
        "secrets_count": len(secrets),
        "secrets_data": secrets,
        "secrets_path": secrets_manager.secrets_path,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/secrets/<secret_name>')
def get_secret(secret_name: str):
    """특정 시크릿 조회"""
    secret_value = secrets_manager.get_secret(secret_name)
    
    return jsonify({
        "secret_name": secret_name,
        "secret_value": secret_value,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """앱 통계 정보"""
    return jsonify({
        "log_counter": log_generator.counter,
        "uptime": "N/A",  # 실제 구현시 시작 시간 추적
        "secrets_loaded": len(secrets_manager.secrets_data),
        "environment_vars": {
            "DB_PASSWORD": "SET" if os.getenv("DB_PASSWORD") else "NOT_SET",
            "POD_NAME": os.getenv("HOSTNAME", "unknown"),
            "NAMESPACE": os.getenv("NAMESPACE", "unknown")
        },
        "timestamp": datetime.now().isoformat()
    })

def start_log_generator():
    """로그 생성기를 백그라운드에서 시작"""
    thread = threading.Thread(target=log_generator.generate_logs, daemon=True)
    thread.start()
    logger.info("Log generator started in background")

if __name__ == '__main__':
    # 시크릿 초기 로드
    secrets_manager.load_secrets()
    
    # 백그라운드 로그 생성 시작
    start_log_generator()
    
    # Flask 앱 실행
    app.run(host='0.0.0.0', port=8000, debug=False)

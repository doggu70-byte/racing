"""
경마 예측 모델 서비스

두 가지 예측 모델:
1. AI 예측 모델 (자동 학습)
2. 사용자 파라미터 예측 모델 (가중치 조절)
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models
import logging

logger = logging.getLogger(__name__)


class PredictionModel:
    """예측 모델 베이스 클래스"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.version = 1.0
        self.created_at = datetime.now()
        
    def predict(self, race_data: Dict) -> List[Dict]:
        """경주 예측 (서브클래스에서 구현)"""
        raise NotImplementedError
        
    def get_accuracy(self) -> float:
        """모델 정확도 반환"""
        cache_key = f"model_accuracy:{self.model_name}"
        return cache.get(cache_key, 0.0)


class AIPredictionModel(PredictionModel):
    """AI 자동 학습 예측 모델"""
    
    def __init__(self):
        super().__init__("AI_AUTO")
        self.features = [
            'recent_wins',      # 최근 승수
            'recent_races',     # 최근 출주 횟수  
            'jockey_rating',    # 기수 레이팅
            'trainer_rating',   # 조교사 레이팅
            'weight_rating',    # 마체중 점수
            'distance_fit',     # 거리 적합도
            'track_condition',  # 트랙 컨디션
            'odds_rating',      # 배당률 점수
        ]
        
    def extract_features(self, horse_data: Dict) -> Dict[str, float]:
        """말 데이터에서 특성 추출 (출전표/성적 API 모두 지원)"""
        try:
            features = {}
            
            # API 데이터 타입 확인 (출전표 vs 성적)
            is_entry_data = 'hrAge' in horse_data  # 출전표 API는 hrAge 필드 있음
            
            if is_entry_data:
                # 출전표 데이터 처리 (예정된 경주)
                features = self._extract_entry_features(horse_data)
            else:
                # 성적 데이터 처리 (완료된 경주)
                features = self._extract_result_features(horse_data)
                
            return features
            
        except Exception as e:
            logger.error(f"특성 추출 오류: {str(e)}")
            return {feature: 50.0 for feature in self.features}
    
    def _extract_entry_features(self, horse_data: Dict) -> Dict[str, float]:
        """출전표 데이터에서 특성 추출"""
        features = {}
        
        # 출전표에서는 과거 성적이 제한적이므로 기본값 사용
        features['recent_wins'] = 2.0  # 평균값
        features['recent_races'] = 10.0  # 평균값  
        features['win_rate'] = 0.2  # 20% 기본 승률
        
        # 기수/조교사 레이팅
        features['jockey_rating'] = self._calculate_person_rating(horse_data.get('jkName', ''))
        features['trainer_rating'] = self._calculate_person_rating(horse_data.get('trName', ''))
        
        # 마체중 점수 (출전표에서는 예상 체중)
        weight_str = horse_data.get('wgHr', '500')
        try:
            weight = float(weight_str.split('(')[0]) if '(' in weight_str else float(weight_str or 500)
            features['weight_rating'] = max(0, 100 - abs(weight - 500) / 5)
        except:
            features['weight_rating'] = 70.0
        
        # 나이 기반 점수 (4-6세가 전성기)
        age = int(horse_data.get('hrAge', 5) or 5)
        if 4 <= age <= 6:
            age_score = 90.0
        elif age == 3 or age == 7:
            age_score = 70.0
        else:
            age_score = 50.0
        features['distance_fit'] = age_score
        
        # 성별 기반 점수 (수말이 일반적으로 유리)
        sex = horse_data.get('hrSex', 'M')
        sex_score = 80.0 if sex == 'M' else 70.0 if sex == 'F' else 60.0
        features['track_condition'] = sex_score
        
        # 배당률 (출전표에는 없으므로 기본값)
        features['odds_rating'] = 50.0
        
        return features
    
    def _extract_result_features(self, horse_data: Dict) -> Dict[str, float]:
        """성적 데이터에서 특성 추출 (기존 로직)"""
        features = {}
        
        # 최근 성적 기반 특성
        recent_wins = int(horse_data.get('win1', 0) or 0)
        recent_races = int(horse_data.get('totCnt1', 0) or 0)
        
        features['recent_wins'] = recent_wins
        features['recent_races'] = recent_races
        features['win_rate'] = recent_wins / max(recent_races, 1)
        
        # 기수/조교사 레이팅
        features['jockey_rating'] = self._calculate_person_rating(horse_data.get('jkName', ''))
        features['trainer_rating'] = self._calculate_person_rating(horse_data.get('trName', ''))
        
        # 마체중 점수 (450-550kg가 적정)
        weight_str = horse_data.get('wgHr', '500')
        try:
            weight = float(weight_str.split('(')[0]) if '(' in weight_str else float(weight_str or 500)
            features['weight_rating'] = max(0, 100 - abs(weight - 500) / 5)
        except:
            features['weight_rating'] = 70.0
        
        # 거리 적합도 (실제 성적 기반)
        features['distance_fit'] = 60.0 + (recent_wins * 5)  # 승수에 따라 조정
        
        # 트랙 컨디션 (실제 성적 반영)
        features['track_condition'] = 50.0 + (features['win_rate'] * 30)
        
        # 배당률 점수 (낮을수록 유리)
        odds = float(horse_data.get('winOdds', 10) or 10)
        features['odds_rating'] = max(0, 100 - odds * 5)
        
        return features
    
    def _calculate_person_rating(self, name: str) -> float:
        """기수/조교사 레이팅 계산 (임시 구현)"""
        if not name:
            return 50.0
        
        # 간단한 해시 기반 점수 (실제로는 성적 데이터 기반으로 계산)
        hash_score = sum(ord(c) for c in name) % 50
        return 30.0 + hash_score
    
    def predict(self, race_data: Dict) -> List[Dict]:
        """AI 모델 예측"""
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return []
            
            predictions = []
            
            for horse in horses:
                features = self.extract_features(horse)
                
                # 간단한 가중치 기반 점수 계산 (실제로는 ML 모델 사용)
                weights = {
                    'recent_wins': 0.25,
                    'win_rate': 0.20, 
                    'jockey_rating': 0.15,
                    'trainer_rating': 0.10,
                    'weight_rating': 0.10,
                    'distance_fit': 0.05,
                    'track_condition': 0.05,
                    'odds_rating': 0.10
                }
                
                # 가중 평균 계산
                total_score = sum(features.get(key, 50) * weight 
                                for key, weight in weights.items())
                
                # 0-100 범위로 정규화
                win_probability = max(0, min(100, total_score))
                
                predictions.append({
                    'horse_name': horse.get('hrName', ''),
                    'horse_no': horse.get('hrNo', ''),
                    'chul_no': horse.get('chulNo', ''),  # 출전번호 추가
                    'win_probability': round(win_probability, 1),
                    'features': features,
                    'rank_prediction': 0  # 나중에 순위 매김
                })
            
            # 승률 기준 순위 매기기
            predictions.sort(key=lambda x: x['win_probability'], reverse=True)
            for i, pred in enumerate(predictions):
                pred['rank_prediction'] = i + 1
                
            return predictions
            
        except Exception as e:
            logger.error(f"AI 예측 오류: {str(e)}")
            return []


class UserParameterModel(PredictionModel):
    """사용자 파라미터 예측 모델"""
    
    def __init__(self, user_weights: Dict[str, float] = None):
        super().__init__("USER_PARAM")
        
        # 기본 가중치
        self.default_weights = {
            'recent_performance': 25.0,  # 최근 성적
            'jockey_skill': 20.0,        # 기수 실력
            'trainer_skill': 15.0,       # 조교사 실력
            'horse_condition': 15.0,     # 말 컨디션
            'distance_experience': 10.0, # 거리 경험
            'track_condition': 8.0,      # 트랙 상태
            'odds_factor': 7.0,          # 배당률 요소
        }
        
        self.user_weights = user_weights or self.default_weights.copy()
    
    def update_weights(self, new_weights: Dict[str, float]):
        """사용자 가중치 업데이트"""
        # 프론트엔드 키를 백엔드 키로 매핑
        key_mapping = {
            'recent_performance': 'recent_performance',
            'horse_rating': 'horse_condition',
            'weight_change': 'track_condition', 
            'jockey_skill': 'jockey_skill',
            'trainer_skill': 'trainer_skill',
            'distance_aptitude': 'distance_experience'
        }
        
        # 매핑된 가중치로 업데이트
        mapped_weights = {}
        for front_key, back_key in key_mapping.items():
            if front_key in new_weights:
                mapped_weights[back_key] = new_weights[front_key]
        
        self.user_weights.update(mapped_weights)
        
        # 가중치 합계가 100이 되도록 정규화
        total = sum(self.user_weights.values())
        if total > 0:
            self.user_weights = {k: (v/total)*100 for k, v in self.user_weights.items()}
            
        logger.info(f"사용자 가중치 업데이트 완료: {self.user_weights}")
    
    def predict(self, race_data: Dict) -> List[Dict]:
        """사용자 파라미터 모델 예측"""
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return []
            
            predictions = []
            
            for horse in horses:
                scores = self._calculate_parameter_scores(horse)
                
                # 사용자 가중치 적용
                weighted_score = sum(scores.get(param, 50) * (weight/100) 
                                   for param, weight in self.user_weights.items())
                
                predictions.append({
                    'horse_name': horse.get('hrName', ''),
                    'horse_no': horse.get('hrNo', ''),
                    'chul_no': horse.get('chulNo', ''),  # 출전번호 추가
                    'win_probability': round(weighted_score, 1),
                    'parameter_scores': scores,
                    'applied_weights': self.user_weights.copy(),
                    'rank_prediction': 0
                })
            
            # 승률 기준 순위 매기기
            predictions.sort(key=lambda x: x['win_probability'], reverse=True)
            for i, pred in enumerate(predictions):
                pred['rank_prediction'] = i + 1
                
            return predictions
            
        except Exception as e:
            logger.error(f"사용자 파라미터 예측 오류: {str(e)}")
            return []
    
    def _calculate_parameter_scores(self, horse: Dict) -> Dict[str, float]:
        """각 파라미터별 점수 계산 (출전표/성적 API 모두 지원)"""
        scores = {}
        
        try:
            # API 데이터 타입 확인 (출전표 vs 성적)
            is_entry_data = 'hrAge' in horse  # 출전표 API는 hrAge 필드 있음
            
            if is_entry_data:
                # 출전표 데이터 처리
                scores = self._calculate_entry_scores(horse)
            else:
                # 성적 데이터 처리 (기존 로직)
                scores = self._calculate_result_scores(horse)
            
        except Exception as e:
            logger.error(f"파라미터 점수 계산 오류: {str(e)}")
            # 기본 점수로 초기화
            for param in self.default_weights.keys():
                scores[param] = 50.0
                
        return scores
    
    def _calculate_entry_scores(self, horse: Dict) -> Dict[str, float]:
        """출전표 데이터로 파라미터 점수 계산"""
        scores = {}
        
        # 최근 성적 (출전표에는 제한적 정보)
        scores['recent_performance'] = 60.0  # 기본값
        
        # 기수 실력 (이름 기반 점수)
        jockey_name = horse.get('jkName', '')
        scores['jockey_skill'] = self._get_person_score(jockey_name)
        
        # 조교사 실력
        trainer_name = horse.get('trName', '')
        scores['trainer_skill'] = self._get_person_score(trainer_name)
        
        # 말 컨디션 (마체중 + 나이 기반)
        weight_str = horse.get('wgHr', '500')
        try:
            weight = float(weight_str.split('(')[0]) if '(' in weight_str else float(weight_str or 500)
            weight_score = max(0, 100 - abs(weight - 500) / 2)
        except:
            weight_score = 70.0
            
        # 나이 보정 (4-6세가 전성기)
        age = int(horse.get('hrAge', 5) or 5)
        if 4 <= age <= 6:
            age_bonus = 10.0
        elif age == 3 or age == 7:
            age_bonus = 0.0
        else:
            age_bonus = -10.0
            
        scores['horse_condition'] = min(100, weight_score + age_bonus)
        
        # 거리 경험 (나이와 성별 기반 추정)
        sex = horse.get('hrSex', 'M')
        base_exp = 70.0 if age >= 4 else 50.0
        sex_bonus = 5.0 if sex == 'M' else 0.0
        scores['distance_experience'] = min(100, base_exp + sex_bonus)
        
        # 트랙 상태 (성별 기반)
        scores['track_condition'] = 75.0 if sex == 'M' else 70.0
        
        # 배당률 요소 (출전표에는 없음)
        scores['odds_factor'] = 50.0
        
        return scores
    
    def _calculate_result_scores(self, horse: Dict) -> Dict[str, float]:
        """성적 데이터로 파라미터 점수 계산 (기존 로직)"""
        scores = {}
        
        # 최근 성적 (승률 기반)
        recent_wins = int(horse.get('win1', 0) or 0)
        recent_races = int(horse.get('totCnt1', 0) or 0)
        win_rate = (recent_wins / max(recent_races, 1)) * 100
        scores['recent_performance'] = min(100, win_rate * 5)  # 20% 승률 = 100점
        
        # 기수 실력 (이름 기반 임시 점수)
        jockey_name = horse.get('jkName', '')
        scores['jockey_skill'] = self._get_person_score(jockey_name)
        
        # 조교사 실력
        trainer_name = horse.get('trName', '')
        scores['trainer_skill'] = self._get_person_score(trainer_name)
        
        # 말 컨디션 (마체중 기반)
        weight_str = horse.get('wgHr', '500')
        try:
            weight = float(weight_str.split('(')[0]) if '(' in weight_str else float(weight_str or 500)
            weight_diff = abs(weight - 500)
            scores['horse_condition'] = max(0, 100 - weight_diff / 2)
        except:
            scores['horse_condition'] = 70.0
        
        # 거리 경험 (성적 기반)
        scores['distance_experience'] = 50.0 + (recent_wins * 3)
        
        # 트랙 상태 (승률 반영)  
        scores['track_condition'] = 50.0 + (win_rate * 2)
        
        # 배당률 요소 (낮을수록 유리)
        odds = float(horse.get('winOdds', 10) or 10)
        scores['odds_factor'] = max(0, min(100, 100 - odds * 3))
        
        return scores
    
    def _get_person_score(self, name: str) -> float:
        """기수/조교사 점수 계산 (임시 구현)"""
        if not name:
            return 50.0
            
        # 실제로는 DB에서 성적 조회
        hash_score = sum(ord(c) for c in name) % 40
        return 40.0 + hash_score


class BettingRecommendationService:
    """승식별 베팅 추천 서비스"""
    
    def __init__(self):
        self.betting_types = {
            '단승': {'name': '단승', 'description': '1위 예측', 'risk': 'high', 'return': 'high'},
            '연승': {'name': '연승', 'description': '1-2위 순서대로 예측', 'risk': 'very_high', 'return': 'very_high'},  
            '복승': {'name': '복승', 'description': '1-2위 순서 무관 예측', 'risk': 'medium', 'return': 'medium'},
            '쌍승': {'name': '쌍승', 'description': '1-3위 중 2마리 예측', 'risk': 'low', 'return': 'low'}
        }
    
    def generate_recommendations(self, ai_predictions: List[Dict], user_predictions: List[Dict]) -> Dict:
        """승식별 베팅 추천 생성"""
        try:
            recommendations = {}
            
            # AI 모델 기반 추천
            ai_top_3 = ai_predictions[:3]
            user_top_3 = user_predictions[:3]
            
            # 단승 (1위 예측)
            recommendations['단승'] = {
                'type': '단승',
                'ai_pick': {
                    'horse': ai_top_3[0]['horse_name'],
                    'probability': ai_top_3[0]['win_probability'],
                    'confidence': 'high' if ai_top_3[0]['win_probability'] > 40 else 'medium'
                },
                'user_pick': {
                    'horse': user_top_3[0]['horse_name'],
                    'probability': user_top_3[0]['win_probability'],
                    'confidence': 'high' if user_top_3[0]['win_probability'] > 50 else 'medium'
                },
                'recommendation': '상위 예측 말의 확률이 높을 때 추천'
            }
            
            # 연승 (1-2위 순서대로)
            recommendations['연승'] = {
                'type': '연승',
                'ai_pick': {
                    'combination': f"{ai_top_3[0]['horse_name']} → {ai_top_3[1]['horse_name']}",
                    'probability': ai_top_3[0]['win_probability'] * ai_top_3[1]['win_probability'] / 100,
                    'confidence': 'low'  # 순서까지 맞추기는 어려움
                },
                'user_pick': {
                    'combination': f"{user_top_3[0]['horse_name']} → {user_top_3[1]['horse_name']}",
                    'probability': user_top_3[0]['win_probability'] * user_top_3[1]['win_probability'] / 100,
                    'confidence': 'low'
                },
                'recommendation': '고위험 고수익, 경험 많은 사용자 추천'
            }
            
            # 복승 (1-2위 순서 무관)
            recommendations['복승'] = {
                'type': '복승',
                'ai_pick': {
                    'combination': f"{ai_top_3[0]['horse_name']} & {ai_top_3[1]['horse_name']}",
                    'probability': (ai_top_3[0]['win_probability'] + ai_top_3[1]['win_probability']) / 2,
                    'confidence': 'medium'
                },
                'user_pick': {
                    'combination': f"{user_top_3[0]['horse_name']} & {user_top_3[1]['horse_name']}",
                    'probability': (user_top_3[0]['win_probability'] + user_top_3[1]['win_probability']) / 2,
                    'confidence': 'medium'
                },
                'recommendation': '단승보다 안전한 선택, 초보자 추천'
            }
            
            # 쌍승 (1-3위 중 2마리)
            top_3_combinations = [
                (ai_top_3[0], ai_top_3[1]),
                (ai_top_3[0], ai_top_3[2]),
                (ai_top_3[1], ai_top_3[2])
            ]
            
            best_ai_combo = max(top_3_combinations, 
                              key=lambda x: x[0]['win_probability'] + x[1]['win_probability'])
            
            user_top_3_combinations = [
                (user_top_3[0], user_top_3[1]),
                (user_top_3[0], user_top_3[2]),
                (user_top_3[1], user_top_3[2])
            ]
            
            best_user_combo = max(user_top_3_combinations,
                                key=lambda x: x[0]['win_probability'] + x[1]['win_probability'])
            
            recommendations['쌍승'] = {
                'type': '쌍승',
                'ai_pick': {
                    'combination': f"{best_ai_combo[0]['horse_name']} & {best_ai_combo[1]['horse_name']}",
                    'probability': (best_ai_combo[0]['win_probability'] + best_ai_combo[1]['win_probability']) / 2,
                    'confidence': 'high'
                },
                'user_pick': {
                    'combination': f"{best_user_combo[0]['horse_name']} & {best_user_combo[1]['horse_name']}",
                    'probability': (best_user_combo[0]['win_probability'] + best_user_combo[1]['win_probability']) / 2,
                    'confidence': 'high'
                },
                'recommendation': '가장 안전한 선택, 초보자와 보수적 베팅 추천'
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"베팅 추천 생성 오류: {str(e)}")
            return {}


class PredictionService:
    """예측 서비스 통합 관리"""
    
    def __init__(self):
        self.ai_model = AIPredictionModel()
        self.user_model = UserParameterModel()
        self.betting_service = BettingRecommendationService()
    
    def get_predictions(self, race_data: Dict, user_weights: Dict = None) -> Dict:
        """두 모델의 예측 결과 및 베팅 추천 반환"""
        try:
            # AI 모델 예측
            ai_predictions = self.ai_model.predict(race_data)
            
            # 사용자 파라미터 모델 예측
            if user_weights:
                self.user_model.update_weights(user_weights)
            user_predictions = self.user_model.predict(race_data)
            
            # 베팅 추천 생성
            betting_recommendations = self.betting_service.generate_recommendations(
                ai_predictions, user_predictions
            )
            
            return {
                'ai_model': {
                    'name': 'AI 자동 예측',
                    'version': self.ai_model.version,
                    'accuracy': self.ai_model.get_accuracy(),
                    'predictions': ai_predictions
                },
                'user_model': {
                    'name': '사용자 설정 예측',
                    'version': self.user_model.version,
                    'weights': self.user_model.user_weights,
                    'predictions': user_predictions
                },
                'betting_recommendations': betting_recommendations,
                'race_info': {
                    'horse_count': len(race_data.get('horses', [])),
                    'predicted_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"예측 서비스 오류: {str(e)}")
            return {
                'error': str(e),
                'ai_model': {'predictions': []},
                'user_model': {'predictions': []},
                'betting_recommendations': {},
                'race_info': {'horse_count': 0}
            }
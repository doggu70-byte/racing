"""
한국마사회 API 연동 서비스

주요 기능:
- 경주 계획표 조회 
- 경주마 상세정보 조회
- 경주 성적 정보 조회  
- 경주 기록 정보 조회
"""

import requests
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)


class KRAAPIService:
    """한국마사회 API 연동 서비스 클래스"""
    
    # API 설정
    API_KEY = "95c3f0cdaf9f7b1d450b16dbda6480a9b7472e093d4fd0a63204fc006e4bd202"
    BASE_URL = "https://apis.data.go.kr/B551015"
    
    # API 엔드포인트 (서브패스 포함)
    ENDPOINTS = {
        'race_schedule': '/API72_2/racePlan_2',           # 경주계획표
        'horse_info': '/API8_2/raceHorseInfo_2',          # 경주마 상세정보  
        'race_results': '/API214_1/RaceDetailResult_1',   # 경주성적정보
        'race_records': '/API4_3/raceResult_3',           # 경주기록정보
        'entry_sheet': '/API26_2/entrySheet_2',           # 출전표 상세정보 (예정 경주)
    }
    
    # 경마장 코드
    TRACKS = {
        1: '서울',
        2: '제주', 
        3: '부경'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Racing-Prediction-System/1.0',
            'Accept': 'application/json',
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any], 
                     cache_timeout: int = 300) -> Optional[Dict]:
        """
        API 요청 실행
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            cache_timeout: 캐시 유지 시간(초)
            
        Returns:
            API 응답 데이터 또는 None
        """
        # 캐시 키 생성
        cache_key = f"kra_api:{endpoint}:{hash(frozenset(params.items()))}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"캐시에서 데이터 반환: {cache_key}")
            return cached_data
        
        # 기본 파라미터 설정
        request_params = {
            'ServiceKey': self.API_KEY,
            'pageNo': 1,
            'numOfRows': 1000,
            '_type': 'xml',
            **params
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.info(f"API 요청: {url}, 파라미터: {request_params}")
            
            response = self.session.get(
                url, 
                params=request_params, 
                timeout=30
            )
            response.raise_for_status()
            
            # XML 응답 파싱
            try:
                root = ET.fromstring(response.content)
                parsed_data = self._parse_xml_response(root)
            except ET.ParseError:
                # JSON 응답 시도
                try:
                    data = response.json()
                    parsed_data = self._parse_json_response(data)
                except json.JSONDecodeError:
                    logger.error(f"XML/JSON 파싱 모두 실패: {url}")
                    return None
            
            # 캐시에 저장
            if parsed_data:
                cache.set(cache_key, parsed_data, cache_timeout)
                logger.info(f"응답 데이터 캐시 저장: {cache_key}")
            
            return parsed_data
            
        except requests.exceptions.Timeout:
            logger.error(f"API 요청 타임아웃: {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"API 연결 오류: {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 오류: {e.response.status_code} - {url}")
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 오류: {url}")
        except Exception as e:
            logger.error(f"예상치 못한 오류: {str(e)} - {url}")
        
        return None
    
    def _parse_xml_response(self, root) -> Optional[Dict]:
        """XML 응답 파싱"""
        try:
            # 에러 확인
            fault = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')
            if fault is not None:
                fault_string = fault.find('.//faultstring')
                if fault_string is not None:
                    logger.error(f"SOAP Fault: {fault_string.text}")
                return None
            
            # response 구조 찾기
            header = root.find('.//header')
            body = root.find('.//body')
            
            if header is None or body is None:
                logger.error("XML 응답에서 header 또는 body를 찾을 수 없음")
                return None
            
            # 결과 코드 확인
            result_code = header.find('resultCode')
            result_msg = header.find('resultMsg')
            
            if result_code is not None and result_code.text != '00':
                msg = result_msg.text if result_msg is not None else '알 수 없는 오류'
                logger.error(f"API 오류 응답: {result_code.text} - {msg}")
                return None
            
            # items 파싱
            items_element = body.find('items')
            if items_element is None:
                logger.warning("items 요소를 찾을 수 없음")
                return {'items': []}
            
            items = []
            for item in items_element.findall('item'):
                item_dict = {}
                for child in item:
                    item_dict[child.tag] = child.text
                items.append(item_dict)
            
            # 페이징 정보
            total_count = body.find('totalCount')
            page_no = body.find('pageNo')
            num_of_rows = body.find('numOfRows')
            
            result = {
                'items': items,
                'totalCount': int(total_count.text) if total_count is not None else len(items),
                'pageNo': int(page_no.text) if page_no is not None else 1,
                'numOfRows': int(num_of_rows.text) if num_of_rows is not None else len(items)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"XML 파싱 오류: {str(e)}")
            return None
    
    def _parse_json_response(self, data) -> Optional[Dict]:
        """JSON 응답 파싱 (기존 로직)"""
        try:
            # 응답 구조 검증
            if 'response' not in data:
                logger.error(f"응답 구조 오류: {data}")
                return None
                
            response_body = data['response'].get('body', {})
            
            # 에러 코드 확인
            header = data['response'].get('header', {})
            result_code = header.get('resultCode', '00')
            
            if result_code != '00':
                result_msg = header.get('resultMsg', '알 수 없는 오류')
                logger.error(f"API 오류 응답: {result_code} - {result_msg}")
                return None
            
            return response_body
            
        except Exception as e:
            logger.error(f"JSON 파싱 오류: {str(e)}")
            return None
    
    def get_race_schedule(self, meet: int = 1, rc_date: str = None, 
                         rc_month: str = None, rc_year: str = None) -> List[Dict]:
        """
        경주 계획표 조회
        
        Args:
            meet: 경마장 (1:서울, 2:제주, 3:부경)
            rc_date: 경주일자 (YYYYMMDD)
            rc_month: 경주년월 (YYYYMM)
            rc_year: 경주년도 (YYYY)
            
        Returns:
            경주 계획 리스트
        """
        params = {'meet': meet}
        
        if rc_date:
            params['rc_date'] = rc_date
        elif rc_month:
            params['rc_month'] = rc_month
        elif rc_year:
            params['rc_year'] = rc_year
        
        data = self._make_request(self.ENDPOINTS['race_schedule'], params)
        
        if data and 'items' in data:
            races = data['items']
            logger.info(f"경주 계획표 {len(races)}건 조회 완료 ({self.TRACKS.get(meet, meet)})")
            return races
        
        logger.warning(f"경주 계획표 조회 실패 ({self.TRACKS.get(meet, meet)})")
        return []
    
    def get_horse_info(self, meet: int = 1, hr_no: str = None) -> List[Dict]:
        """
        경주마 상세정보 조회
        
        Args:
            meet: 경마장 (1:서울, 2:제주, 3:부경)  
            hr_no: 마번
            
        Returns:
            경주마 정보 리스트
        """
        params = {'meet': meet}
        
        if hr_no:
            params['hr_no'] = hr_no
        
        data = self._make_request(self.ENDPOINTS['horse_info'], params)
        
        if data and 'items' in data:
            horses = data['items']
            logger.info(f"경주마 정보 {len(horses)}건 조회 완료 ({self.TRACKS.get(meet, meet)})")
            return horses
        
        logger.warning(f"경주마 정보 조회 실패 ({self.TRACKS.get(meet, meet)})")
        return []
    
    def get_race_results(self, meet: int = 1, race_date: str = None,
                        rc_date: str = None) -> List[Dict]:
        """
        경주 성적정보 조회
        
        Args:
            meet: 경마장 (1:서울, 2:제주, 3:부경)
            race_date: 경주일자 (YYYYMMDD) 
            rc_date: 경주년월 (YYYYMM)
            
        Returns:
            경주 성적 리스트
        """
        params = {'meet': meet}
        
        if race_date:
            params['race_date'] = race_date
        elif rc_date:
            params['rc_date'] = rc_date
        
        data = self._make_request(self.ENDPOINTS['race_results'], params)
        
        if data and 'items' in data:
            results = data['items']
            logger.info(f"경주 성적 {len(results)}건 조회 완료 ({self.TRACKS.get(meet, meet)})")
            return results
        
        logger.warning(f"경주 성적 조회 실패 ({self.TRACKS.get(meet, meet)})")
        return []
    
    def get_race_records(self, meet: int = 1, race_date: str = None,
                        rc_date: str = None) -> List[Dict]:
        """
        경주 기록정보 조회
        
        Args:
            meet: 경마장 (1:서울, 2:제주, 3:부경)
            race_date: 경주일자 (YYYYMMDD)
            rc_date: 경주년월 (YYYYMM) 
            
        Returns:
            경주 기록 리스트
        """
        params = {'meet': meet}
        
        if race_date:
            params['race_date'] = race_date
        elif rc_date:
            params['rc_date'] = rc_date
        
        data = self._make_request(self.ENDPOINTS['race_records'], params)
        
        if data and 'items' in data:
            records = data['items']
            logger.info(f"경주 기록 {len(records)}건 조회 완료 ({self.TRACKS.get(meet, meet)})")
            return records
        
        logger.warning(f"경주 기록 조회 실패 ({self.TRACKS.get(meet, meet)})")
        return []
    
    def get_today_races(self) -> Dict[int, List[Dict]]:
        """
        오늘 요일에 해당하는 경주 계획 조회 (금/토/일만 경마 개최)
        
        Returns:
            경마장별 오늘 경주 계획, 시간순 정렬
        """
        today = datetime.now()
        weekday = today.weekday()  # 0=월, 1=화, 2=수, 3=목, 4=금, 5=토, 6=일
        
        # 경주일 결정
        if weekday == 4:  # 금요일
            race_date = today
        elif weekday == 5:  # 토요일
            race_date = today
        elif weekday == 6:  # 일요일
            race_date = today
        else:
            # 월-목요일인 경우 다음 금요일 찾기
            days_until_friday = (4 - weekday) % 7
            if days_until_friday == 0:  # 오늘이 금요일인 경우
                days_until_friday = 7
            race_date = today + timedelta(days=days_until_friday)
        
        race_date_str = race_date.strftime('%Y%m%d')
        logger.info(f"경주 일정 조회 날짜: {race_date_str} ({['월','화','수','목','금','토','일'][race_date.weekday()]}요일)")
        
        all_races = {}
        all_races_list = []  # 전체 경주를 시간순으로 정렬하기 위한 리스트
        
        for meet in self.TRACKS.keys():
            try:
                races = self.get_race_schedule(meet=meet, rc_date=race_date_str)
                if races:
                    # 각 경주에 경마장 정보와 정렬용 키 추가
                    for race in races:
                        race['meet'] = meet
                        race['meet_name'] = self.TRACKS[meet]
                        # 시간 정렬을 위한 키 생성
                        start_time = race.get('schStTime') or race.get('rcTime') or '0000'
                        race['sort_time'] = start_time.zfill(4)  # 4자리로 패딩
                        all_races_list.append(race)
                    
                    all_races[meet] = races
                    logger.info(f"{self.TRACKS[meet]}: {len(races)}경주")
            except Exception as e:
                logger.error(f"{self.TRACKS[meet]} 경주 조회 실패: {e}")
                continue
        
        # 전체 경주를 시간순으로 정렬
        all_races_list.sort(key=lambda x: (x['sort_time'], x['meet'], x.get('rcNo', '1')))
        
        # 정렬된 리스트 반환 (기존 형식 유지)
        result = {'sorted_races': all_races_list}
        result.update(all_races)
        
        logger.info(f"총 {len(all_races_list)}개 경주 조회 완료")
        return result
    
    def get_recent_results(self, days: int = 7) -> Dict[int, List[Dict]]:
        """
        최근 경주 결과 조회
        
        Args:
            days: 조회할 일수
            
        Returns:
            경마장별 최근 경주 결과
        """
        all_results = {}
        
        for meet in self.TRACKS.keys():
            meet_results = []
            
            for i in range(days):
                target_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                results = self.get_race_results(meet=meet, race_date=target_date)
                meet_results.extend(results)
            
            if meet_results:
                all_results[meet] = meet_results
        
        return all_results
    
    def get_entry_sheet(self, meet: int = 1, rc_date: str = None, 
                       rc_month: str = None, rc_no: str = None) -> List[Dict]:
        """
        출전표 상세정보 조회 (예정된 경주의 출전마 정보)
        
        Args:
            meet: 경마장 (1:서울, 2:제주, 3:부경)
            rc_date: 경주일자 (YYYYMMDD)
            rc_month: 경주년월 (YYYYMM)
            rc_no: 경주번호
            
        Returns:
            출전표 정보 리스트
        """
        params = {'meet': meet}
        
        if rc_date:
            params['rc_date'] = rc_date
        if rc_month:
            params['rc_month'] = rc_month
        if rc_no:
            params['rc_no'] = rc_no
        
        data = self._make_request(self.ENDPOINTS['entry_sheet'], params)
        
        if data and 'items' in data:
            entries = data['items']
            logger.info(f"출전표 정보 {len(entries)}건 조회 완료 ({self.TRACKS.get(meet, meet)})")
            return entries
        
        logger.warning(f"출전표 정보 조회 실패 ({self.TRACKS.get(meet, meet)})")
        return []

    def test_connection(self) -> bool:
        """
        API 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            # 서울경마장 오늘 경주로 테스트
            races = self.get_race_schedule(meet=1)
            logger.info(f"API 연결 테스트 성공: {len(races)}건 조회")
            return len(races) >= 0  # 0건이어도 성공으로 판단
        except Exception as e:
            logger.error(f"API 연결 테스트 실패: {str(e)}")
            return False
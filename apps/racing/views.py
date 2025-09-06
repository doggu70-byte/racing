from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from .services import KRAAPIService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def index(request):
    """메인 대시보드 페이지"""
    context = {
        'title': '경마 예측 시스템',
        'current_time': timezone.now(),
    }
    return render(request, 'racing/index.html', context)


@require_http_methods(["GET"])
def api_test(request):
    """API 연결 테스트"""
    try:
        api_service = KRAAPIService()
        success = api_service.test_connection()
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'API 연결 성공'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'API 연결 실패'
            }, status=500)
            
    except Exception as e:
        logger.error(f"API 테스트 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'오류 발생: {str(e)}'
        }, status=500)


@require_http_methods(["GET"]) 
def today_races(request):
    """오늘의 경주 정보 조회"""
    try:
        api_service = KRAAPIService()
        races = api_service.get_today_races()
        
        return JsonResponse({
            'success': True,
            'data': races,
            'tracks': KRAAPIService.TRACKS
        })
        
    except Exception as e:
        logger.error(f"오늘 경주 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'오류 발생: {str(e)}'
        }, status=500)


def schedule_view(request):
    """경주 일정 조회 페이지"""
    context = {
        'title': '경주 일정 조회',
        'tracks': KRAAPIService.TRACKS
    }
    return render(request, 'racing/schedule.html', context)


@require_http_methods(["GET"])
def api_schedule_data(request):
    """AJAX로 경주 일정 데이터 조회"""
    try:
        api_service = KRAAPIService()
        
        # 파라미터 받기
        meet = int(request.GET.get('meet', 1))  # 기본값: 서울
        date = request.GET.get('date', '')
        
        if not date:
            # 기본값: 최근 금요일 찾기
            today = datetime.now()
            days_since_friday = (today.weekday() - 4) % 7
            if days_since_friday == 0 and today.hour < 18:  # 오늘이 금요일인데 오후 6시 전이면 지난 주 금요일
                days_since_friday = 7
            last_friday = today - timedelta(days=days_since_friday)
            date = last_friday.strftime('%Y%m%d')
        
        # 금,토,일 여부 확인
        date_obj = datetime.strptime(date, '%Y%m%d')
        weekday = date_obj.weekday()  # 0=월요일, 6=일요일
        
        if weekday not in [4, 5, 6]:  # 금(4), 토(5), 일(6)이 아닌 경우
            return JsonResponse({
                'success': False,
                'error': f'{date[:4]}-{date[4:6]}-{date[6:8]}은 경마가 없는 날입니다. (금, 토, 일요일만 경마 개최)'
            })
        
        # API 호출
        races = api_service.get_race_schedule(meet=meet, rc_date=date)
        
        return JsonResponse({
            'success': True,
            'data': races,
            'meet': api_service.TRACKS.get(meet, str(meet)),
            'date': date,
            'formatted_date': f"{date[:4]}-{date[4:6]}-{date[6:8]}",
            'count': len(races)
        })
        
    except Exception as e:
        logger.error(f"경주 일정 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def api_race_results(request):
    """AJAX로 경주 성적 데이터 조회"""
    try:
        api_service = KRAAPIService()
        
        # 파라미터 받기
        meet = int(request.GET.get('meet', 1))
        date = request.GET.get('date', '')
        race_no = request.GET.get('race_no', '')
        
        if not date:
            return JsonResponse({
                'success': False,
                'error': '날짜가 필요합니다.'
            })
        
        # API 호출
        results = api_service.get_race_results(meet=meet, race_date=date)
        
        # 특정 경주번호가 지정된 경우 필터링
        if race_no:
            results = [r for r in results if r.get('rcNo') == race_no]
        
        return JsonResponse({
            'success': True,
            'data': results,
            'meet': api_service.TRACKS.get(meet, str(meet)),
            'date': date,
            'formatted_date': f"{date[:4]}-{date[4:6]}-{date[6:8]}",
            'race_no': race_no,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"경주 성적 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def api_race_horses(request):
    """AJAX로 특정 경주의 출전마 리스트 조회"""
    try:
        api_service = KRAAPIService()
        
        # 파라미터 받기
        meet = int(request.GET.get('meet', 1))
        date = request.GET.get('date', '')
        race_no = request.GET.get('race_no', '')
        
        if not date or not race_no:
            return JsonResponse({
                'success': False,
                'error': '날짜와 경주번호가 필요합니다.'
            })
        
        # 현재 날짜와 비교하여 예정/완료 경주 판단
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        is_future_race = date >= today
        
        sorted_horses = []
        
        if is_future_race:
            # 예정된 경주: 출전표 API 사용
            logger.info(f"예정 경주 - 출전표 API 사용: {meet}, {date}, {race_no}")
            entries = api_service.get_entry_sheet(meet=meet, rc_date=date, rc_no=race_no)
            
            # 해당 경주번호의 출전마만 필터링
            race_horses = [e for e in entries if e.get('rcNo') == race_no]
            
            # 출전번호순 정렬
            sorted_horses = sorted(race_horses, key=lambda x: int(x.get('chulNo', 0)))
            
        else:
            # 완료된 경주: 기존 성적 API 사용
            logger.info(f"완료 경주 - 성적 API 사용: {meet}, {date}, {race_no}")
            results = api_service.get_race_results(meet=meet, race_date=date)
            
            # 특정 경주번호와 날짜에 해당하는 말들만 필터링
            race_horses_raw = [r for r in results if r.get('rcNo') == race_no and r.get('rcDate') == date]
            
            # 출전번호별로 중복 제거
            race_horses = {}
            for horse in race_horses_raw:
                chul_no = horse.get('chulNo')
                if chul_no and chul_no not in race_horses:
                    race_horses[chul_no] = horse
            
            # 출전번호순으로 정렬
            sorted_horses = [race_horses[chul_no] for chul_no in sorted(race_horses.keys(), key=lambda x: int(x))]
        
        return JsonResponse({
            'success': True,
            'data': sorted_horses,
            'meet': api_service.TRACKS.get(meet, str(meet)),
            'date': date,
            'formatted_date': f"{date[:4]}-{date[4:6]}-{date[6:8]}",
            'race_no': race_no,
            'count': len(sorted_horses),
            'is_future_race': is_future_race
        })
        
    except Exception as e:
        logger.error(f"출전마 리스트 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def api_horse_detail(request):
    """AJAX로 경주마 상세정보 조회"""
    try:
        api_service = KRAAPIService()
        
        # 파라미터 받기
        meet = int(request.GET.get('meet', 1))
        hr_no = request.GET.get('hr_no', '')
        hr_name = request.GET.get('hr_name', '')
        
        if not hr_no and not hr_name:
            return JsonResponse({
                'success': False,
                'error': '마번 또는 마명이 필요합니다.'
            })
        
        # API 호출
        horses = api_service.get_horse_info(meet=meet, hr_no=hr_no)
        
        # 마명으로 검색한 경우 필터링
        if hr_name and not hr_no:
            horses = [h for h in horses if h.get('hrName') == hr_name]
        
        return JsonResponse({
            'success': True,
            'data': horses,
            'meet': api_service.TRACKS.get(meet, str(meet)),
            'hr_no': hr_no,
            'hr_name': hr_name,
            'count': len(horses)
        })
        
    except Exception as e:
        logger.error(f"경주마 상세정보 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def prediction_view(request):
    """예측 모델 페이지"""
    context = {
        'title': '경마 예측 모델',
        'tracks': KRAAPIService.TRACKS
    }
    return render(request, 'racing/prediction.html', context)


@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_race_prediction(request):
    """AJAX로 경주 예측 수행"""
    try:
        from .services.prediction_models import PredictionService
        import json
        
        # 파라미터 받기
        meet = int(request.GET.get('meet', request.POST.get('meet', 1)))
        date = request.GET.get('date', request.POST.get('date', ''))
        race_no = request.GET.get('race_no', request.POST.get('race_no', ''))
        
        if not date or not race_no:
            return JsonResponse({
                'success': False,
                'error': '날짜와 경주번호가 필요합니다.'
            })
        
        # 경주 데이터 조회 (미래/과거 경주 자동 판단)
        api_service = KRAAPIService()
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        is_future_race = date >= today
        
        race_horses = []
        
        if is_future_race:
            # 예정된 경주: 출전표 API 사용
            logger.info(f"예정 경주 예측 - 출전표 API 사용: {meet}, {date}, {race_no}")
            entries = api_service.get_entry_sheet(meet=meet, rc_date=date, rc_no=race_no)
            
            # 해당 경주번호의 출전마만 필터링
            race_horses_raw = [e for e in entries if e.get('rcNo') == race_no]
            
            # 출전번호순 정렬
            race_horses = sorted(race_horses_raw, key=lambda x: int(x.get('chulNo', 0)))
            
        else:
            # 완료된 경주: 기존 성적 API 사용
            logger.info(f"완료 경주 예측 - 성적 API 사용: {meet}, {date}, {race_no}")
            race_results = api_service.get_race_results(meet=meet, race_date=date)
            
            # 특정 경주번호와 날짜에 해당하는 말들만 필터링
            race_horses_raw = [r for r in race_results if r.get('rcNo') == race_no and r.get('rcDate') == date]
            
            # 출전번호별로 중복 제거
            race_horses_dict = {}
            for horse in race_horses_raw:
                chul_no = horse.get('chulNo')
                if chul_no and chul_no not in race_horses_dict:
                    race_horses_dict[chul_no] = horse
            
            # 출전번호순으로 정렬된 리스트
            race_horses = [race_horses_dict[chul_no] for chul_no in sorted(race_horses_dict.keys(), key=lambda x: int(x))]
        
        if not race_horses:
            return JsonResponse({
                'success': False,
                'error': '해당 경주의 출전마 정보를 찾을 수 없습니다.'
            })
        
        # 사용자 가중치 (POST 요청인 경우)
        user_weights = None
        if request.method == 'POST':
            try:
                # POST 데이터에서 user_weights 파라미터 추출
                user_weights_str = request.POST.get('user_weights')
                if user_weights_str:
                    user_weights = json.loads(user_weights_str)
                    logger.info(f"사용자 가중치 적용: {user_weights}")
                else:
                    logger.info("사용자 가중치 없음, 기본 가중치 사용")
            except Exception as e:
                logger.error(f"사용자 가중치 파싱 오류: {e}")
                user_weights = None
        
        # 예측 수행
        race_data = {'horses': race_horses}
        prediction_service = PredictionService()
        predictions = prediction_service.get_predictions(race_data, user_weights)
        
        return JsonResponse({
            'success': True,
            'data': predictions,
            'meet': api_service.TRACKS.get(meet, str(meet)),
            'date': date,
            'formatted_date': f"{date[:4]}-{date[4:6]}-{date[6:8]}",
            'race_no': race_no,
            'is_future_race': is_future_race,
            'data_source': 'entry_sheet' if is_future_race else 'race_results',
            'horse_count': len(race_horses)
        })
        
    except Exception as e:
        logger.error(f"경주 예측 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
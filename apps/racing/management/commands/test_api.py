"""
한국마사회 API 테스트 명령어
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.racing.services import KRAAPIService
import json
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = '한국마사회 API 데이터 수집 테스트'

    def add_arguments(self, parser):
        parser.add_argument(
            '--meet',
            type=int,
            default=1,
            help='경마장 (1:서울, 2:제주, 3:부경)'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='경주일자 (YYYYMMDD)'
        )
        parser.add_argument(
            '--month',
            type=str, 
            help='경주년월 (YYYYMM)'
        )
        parser.add_argument(
            '--api',
            type=str,
            default='results',
            choices=['schedule', 'horses', 'results', 'records', 'all'],
            help='테스트할 API (schedule/horses/results/records/all)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏇 한국마사회 API 테스트 시작')
        )
        
        api_service = KRAAPIService()
        meet = options['meet']
        meet_name = api_service.TRACKS.get(meet, str(meet))
        
        self.stdout.write(f"경마장: {meet_name} ({meet})")
        
        # 날짜 설정
        if options['date']:
            date_param = options['date']
            self.stdout.write(f"조회 날짜: {date_param}")
        elif options['month']:
            date_param = options['month']
            self.stdout.write(f"조회 월: {date_param}")
        else:
            # 기본값: 최근 7일 전
            date_param = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
            self.stdout.write(f"기본 조회 날짜 (7일 전): {date_param}")
        
        # API 테스트 실행
        if options['api'] == 'all':
            self.test_all_apis(api_service, meet, date_param)
        else:
            self.test_single_api(api_service, meet, date_param, options['api'])

    def test_all_apis(self, api_service, meet, date_param):
        """모든 API 테스트"""
        apis = ['schedule', 'horses', 'results', 'records']
        
        for api_type in apis:
            self.stdout.write(f"\n{'='*50}")
            self.test_single_api(api_service, meet, date_param, api_type)

    def test_single_api(self, api_service, meet, date_param, api_type):
        """단일 API 테스트"""
        self.stdout.write(f"\n📊 {api_type.upper()} API 테스트")
        self.stdout.write("-" * 30)
        
        try:
            if api_type == 'schedule':
                if len(date_param) == 6:  # YYYYMM
                    data = api_service.get_race_schedule(meet=meet, rc_month=date_param)
                else:  # YYYYMMDD
                    data = api_service.get_race_schedule(meet=meet, rc_date=date_param)
                    
            elif api_type == 'horses':
                data = api_service.get_horse_info(meet=meet)
                
            elif api_type == 'results':
                if len(date_param) == 6:  # YYYYMM
                    data = api_service.get_race_results(meet=meet, rc_date=date_param)
                else:  # YYYYMMDD
                    data = api_service.get_race_results(meet=meet, race_date=date_param)
                    
            elif api_type == 'records':
                if len(date_param) == 6:  # YYYYMM
                    data = api_service.get_race_records(meet=meet, rc_date=date_param)
                else:  # YYYYMMDD
                    data = api_service.get_race_records(meet=meet, race_date=date_param)
            
            # 결과 출력
            self.stdout.write(f"✅ 조회 성공: {len(data)}건")
            
            if data:
                self.stdout.write("\n📝 첫 번째 데이터 샘플:")
                sample = data[0]
                
                # 주요 필드만 출력
                important_fields = self.get_important_fields(api_type)
                for field in important_fields:
                    if field in sample:
                        value = sample[field]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        self.stdout.write(f"  {field}: {value}")
                
                if len(data) > 1:
                    self.stdout.write(f"\n📊 총 {len(data)}건의 데이터가 있습니다.")
            else:
                self.stdout.write("❌ 조회된 데이터가 없습니다.")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ {api_type} API 오류: {str(e)}")
            )

    def get_important_fields(self, api_type):
        """API 타입별 중요 필드 반환"""
        fields = {
            'schedule': ['rcDate', 'rcNo', 'rcName', 'rcDist', 'rcTime', 'meet'],
            'horses': ['hrName', 'hrNo', 'age', 'sex', 'jkName', 'trName'],
            'results': ['rcDate', 'rcNo', 'ord', 'hrName', 'hrNo', 'rcTime', 'jkName'],
            'records': ['rcDate', 'rcNo', 'hrName', 'rcRecord', 'ord']
        }
        return fields.get(api_type, ['rcDate', 'hrName', 'rcNo'])

    def test_connection(self, api_service):
        """API 연결 테스트"""
        self.stdout.write("\n🔗 API 연결 테스트 중...")
        
        if api_service.test_connection():
            self.stdout.write(self.style.SUCCESS("✅ API 연결 성공"))
        else:
            self.stdout.write(self.style.ERROR("❌ API 연결 실패"))
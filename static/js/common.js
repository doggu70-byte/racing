/**
 * 경마 예측 시스템 공통 JavaScript
 * jQuery 3.6+ 기반
 */

(function($) {
    'use strict';

    // 네임스페이스 정의
    window.RacingSystem = window.RacingSystem || {};

    /**
     * 공통 유틸리티 함수들
     */
    const Utils = {
        
        /**
         * 날짜 포맷팅
         * @param {Date|string} date - 날짜 객체 또는 문자열
         * @param {string} format - 포맷 ('YYYY-MM-DD', 'YYYY-MM-DD HH:mm' 등)
         * @returns {string} 포맷된 날짜 문자열
         */
        formatDate: function(date, format = 'YYYY-MM-DD') {
            if (!date) return '-';
            
            const d = new Date(date);
            if (isNaN(d.getTime())) return '-';
            
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const hours = String(d.getHours()).padStart(2, '0');
            const minutes = String(d.getMinutes()).padStart(2, '0');
            const seconds = String(d.getSeconds()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes)
                .replace('ss', seconds);
        },

        /**
         * 숫자 포맷팅 (천 단위 구분)
         * @param {number} num - 숫자
         * @param {number} decimals - 소수점 자리수
         * @returns {string} 포맷된 숫자 문자열
         */
        formatNumber: function(num, decimals = 0) {
            if (isNaN(num)) return '-';
            
            return Number(num).toLocaleString('ko-KR', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        },

        /**
         * 퍼센트 포맷팅
         * @param {number} num - 숫자 (0-1 범위)
         * @param {number} decimals - 소수점 자리수
         * @returns {string} 퍼센트 문자열
         */
        formatPercent: function(num, decimals = 1) {
            if (isNaN(num)) return '-';
            
            return (num * 100).toFixed(decimals) + '%';
        },

        /**
         * 안전한 문자열 변환
         * @param {*} value - 변환할 값
         * @param {string} defaultValue - 기본값
         * @returns {string} 문자열
         */
        safeString: function(value, defaultValue = '-') {
            if (value === null || value === undefined || value === '') {
                return defaultValue;
            }
            return String(value);
        },

        /**
         * 디바운스 함수
         * @param {Function} func - 실행할 함수
         * @param {number} wait - 대기 시간 (ms)
         * @returns {Function} 디바운스된 함수
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * 쿠키 값 가져오기
         * @param {string} name - 쿠키 이름
         * @returns {string|null} 쿠키 값
         */
        getCookie: function(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        /**
         * 로컬 스토리지 안전 저장
         * @param {string} key - 키
         * @param {*} value - 값
         */
        setStorage: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('로컬 스토리지 저장 실패:', e);
            }
        },

        /**
         * 로컬 스토리지 안전 읽기
         * @param {string} key - 키
         * @param {*} defaultValue - 기본값
         * @returns {*} 저장된 값 또는 기본값
         */
        getStorage: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('로컬 스토리지 읽기 실패:', e);
                return defaultValue;
            }
        },

        /**
         * URL 쿼리 파라미터 파싱
         * @param {string} url - URL (기본값: 현재 페이지)
         * @returns {Object} 쿼리 파라미터 객체
         */
        parseQuery: function(url = window.location.href) {
            const params = {};
            const urlObj = new URL(url);
            
            for (const [key, value] of urlObj.searchParams) {
                params[key] = value;
            }
            
            return params;
        }
    };

    /**
     * UI 관련 함수들
     */
    const UI = {
        
        /**
         * 로딩 상태 표시
         * @param {jQuery|string} element - 요소 선택자 또는 jQuery 객체
         * @param {string} text - 로딩 텍스트
         */
        showLoading: function(element, text = '처리 중...') {
            const $element = $(element);
            const originalContent = $element.html();
            
            $element
                .data('original-content', originalContent)
                .html(`
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    ${text}
                `)
                .prop('disabled', true)
                .addClass('loading');
        },

        /**
         * 로딩 상태 해제
         * @param {jQuery|string} element - 요소 선택자 또는 jQuery 객체
         */
        hideLoading: function(element) {
            const $element = $(element);
            const originalContent = $element.data('original-content');
            
            if (originalContent) {
                $element
                    .html(originalContent)
                    .prop('disabled', false)
                    .removeClass('loading');
            }
        },

        /**
         * 토스트 메시지 표시
         * @param {string} message - 메시지 내용
         * @param {string} type - 메시지 타입 ('success', 'error', 'warning', 'info')
         * @param {number} delay - 표시 시간 (ms)
         */
        showToast: function(message, type = 'info', delay = 5000) {
            const typeClasses = {
                'success': 'text-bg-success',
                'error': 'text-bg-danger',
                'warning': 'text-bg-warning',
                'info': 'text-bg-info'
            };
            
            const iconClasses = {
                'success': 'fa-check-circle',
                'error': 'fa-exclamation-triangle',
                'warning': 'fa-exclamation-circle',
                'info': 'fa-info-circle'
            };
            
            const toastClass = typeClasses[type] || 'text-bg-info';
            const iconClass = iconClasses[type] || 'fa-info-circle';
            
            const toastHtml = `
                <div class="toast ${toastClass}" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas ${iconClass} me-2"></i>
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                                data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            `;
            
            const $toast = $(toastHtml);
            $('.toast-container').append($toast);
            
            const toast = new bootstrap.Toast($toast[0], { delay: delay });
            toast.show();
            
            // 토스트가 숨겨진 후 DOM에서 제거
            $toast.on('hidden.bs.toast', function() {
                $(this).remove();
            });
        },

        /**
         * 확인 대화상자
         * @param {string} message - 확인 메시지
         * @param {string} title - 제목
         * @returns {Promise<boolean>} 확인 여부
         */
        confirm: function(message, title = '확인') {
            return new Promise((resolve) => {
                const modalHtml = `
                    <div class="modal fade" id="confirmModal" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">${title}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <p>${message}</p>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                                    <button type="button" class="btn btn-primary" id="confirmBtn">확인</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                const $modal = $(modalHtml);
                $('body').append($modal);
                
                const modal = new bootstrap.Modal($modal[0]);
                
                $modal.find('#confirmBtn').on('click', function() {
                    modal.hide();
                    resolve(true);
                });
                
                $modal.on('hidden.bs.modal', function() {
                    $(this).remove();
                    resolve(false);
                });
                
                modal.show();
            });
        },

        /**
         * 스크롤 애니메이션
         * @param {jQuery|string} target - 스크롤할 대상
         * @param {number} duration - 애니메이션 시간
         */
        scrollTo: function(target, duration = 500) {
            const $target = $(target);
            if ($target.length) {
                $('html, body').animate({
                    scrollTop: $target.offset().top - 100
                }, duration);
            }
        },

        /**
         * 테이블 정렬 기능
         * @param {jQuery|string} table - 테이블 선택자
         */
        enableTableSort: function(table) {
            $(table).find('th[data-sort]').addClass('sortable').click(function() {
                const $th = $(this);
                const sortKey = $th.data('sort');
                const sortOrder = $th.hasClass('sort-asc') ? 'desc' : 'asc';
                
                // 모든 헤더에서 정렬 클래스 제거
                $th.siblings().removeClass('sort-asc sort-desc');
                
                // 현재 헤더에 정렬 클래스 추가
                $th.removeClass('sort-asc sort-desc').addClass(`sort-${sortOrder}`);
                
                // 정렬 실행
                const $tbody = $th.closest('table').find('tbody');
                const rows = $tbody.find('tr').get();
                
                rows.sort(function(a, b) {
                    const aVal = $(a).find(`[data-sort="${sortKey}"]`).text();
                    const bVal = $(b).find(`[data-sort="${sortKey}"]`).text();
                    
                    if (sortOrder === 'asc') {
                        return aVal.localeCompare(bVal, 'ko', { numeric: true });
                    } else {
                        return bVal.localeCompare(aVal, 'ko', { numeric: true });
                    }
                });
                
                $tbody.empty().append(rows);
            });
        }
    };

    /**
     * AJAX 관련 함수들
     */
    const API = {
        
        /**
         * 기본 AJAX 설정
         */
        setup: function() {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    // CSRF 토큰 자동 추가
                    if (!this.crossDomain && !/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", Utils.getCookie('csrftoken'));
                    }
                },
                error: function(xhr, status, error) {
                    let message = 'AJAX 요청 중 오류가 발생했습니다.';
                    
                    try {
                        const response = JSON.parse(xhr.responseText);
                        message = response.message || message;
                    } catch (e) {
                        if (xhr.status === 404) {
                            message = '요청한 리소스를 찾을 수 없습니다.';
                        } else if (xhr.status === 403) {
                            message = '접근 권한이 없습니다.';
                        } else if (xhr.status >= 500) {
                            message = '서버 오류가 발생했습니다.';
                        }
                    }
                    
                    UI.showToast(message, 'error');
                }
            });
        },

        /**
         * GET 요청
         * @param {string} url - 요청 URL
         * @param {Object} data - 요청 데이터
         * @returns {Promise} jQuery Promise 객체
         */
        get: function(url, data = {}) {
            return $.get(url, data);
        },

        /**
         * POST 요청
         * @param {string} url - 요청 URL
         * @param {Object} data - 요청 데이터
         * @returns {Promise} jQuery Promise 객체
         */
        post: function(url, data = {}) {
            return $.post(url, data);
        },

        /**
         * JSON 요청
         * @param {string} url - 요청 URL
         * @param {Object} options - 요청 옵션
         * @returns {Promise} jQuery Promise 객체
         */
        json: function(url, options = {}) {
            const defaultOptions = {
                method: 'GET',
                dataType: 'json',
                contentType: 'application/json'
            };
            
            return $.ajax(url, { ...defaultOptions, ...options });
        }
    };

    // 전역 네임스페이스에 추가
    window.RacingSystem.Utils = Utils;
    window.RacingSystem.UI = UI;
    window.RacingSystem.API = API;

    // DOM 준비 시 초기화
    $(document).ready(function() {
        // AJAX 설정
        API.setup();
        
        // 전역 이벤트 리스너
        $(document)
            .on('click', '[data-toggle="tooltip"]', function() {
                $(this).tooltip();
            })
            .on('click', '[data-confirm]', function(e) {
                e.preventDefault();
                const message = $(this).data('confirm');
                UI.confirm(message).then(function(result) {
                    if (result) {
                        window.location = $(e.target).attr('href');
                    }
                });
            });
        
        // 뒤로가기 버튼
        $('[data-action="back"]').on('click', function(e) {
            e.preventDefault();
            window.history.back();
        });
        
        // 페이지 상단으로 스크롤
        $('[data-action="scroll-top"]').on('click', function(e) {
            e.preventDefault();
            UI.scrollTo('body');
        });
        
        console.log('Racing System 공통 JavaScript 초기화 완료');
    });

})(jQuery);
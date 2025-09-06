/**
 * 경마 예측 시스템 공통 모달창 시스템
 * Bootstrap 5 Modal 기반
 */

(function($) {
    'use strict';

    // 모달 관리자 클래스
    class ModalManager {
        constructor() {
            this.modals = new Map();
            this.init();
        }

        /**
         * 초기화
         */
        init() {
            // 기본 모달 템플릿 생성
            this.createBaseModal();
            
            // 이벤트 리스너 설정
            this.setupEventListeners();
        }

        /**
         * 기본 모달 템플릿 생성
         */
        createBaseModal() {
            if ($('#commonModal').length === 0) {
                const modalHtml = `
                    <div class="modal fade" id="commonModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="commonModalTitle">알림</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body" id="commonModalBody">
                                    <!-- 동적 내용 -->
                                </div>
                                <div class="modal-footer" id="commonModalFooter">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                $('body').append(modalHtml);
            }
        }

        /**
         * 이벤트 리스너 설정
         */
        setupEventListeners() {
            // 모달 닫힐 때 정리
            $(document).on('hidden.bs.modal', '.modal', (e) => {
                const modalId = $(e.target).attr('id');
                if (modalId && modalId !== 'commonModal') {
                    this.cleanup(modalId);
                }
            });
        }

        /**
         * 상세 정보 모달 표시
         * @param {string} title - 모달 제목
         * @param {string|Object} content - 모달 내용 (HTML 문자열 또는 데이터 객체)
         * @param {Object} options - 추가 옵션
         */
        showDetailModal(title, content, options = {}) {
            const defaultOptions = {
                size: 'lg',
                backdrop: true,
                keyboard: true,
                focus: true
            };
            
            const config = { ...defaultOptions, ...options };
            
            // 모달 내용 구성
            let bodyHtml = '';
            
            if (typeof content === 'string') {
                bodyHtml = content;
            } else if (typeof content === 'object') {
                bodyHtml = this.renderObjectAsTable(content);
            }
            
            this.showModal('detailModal', {
                title: title,
                body: bodyHtml,
                size: config.size,
                buttons: [
                    {
                        text: '닫기',
                        class: 'btn-secondary',
                        dismiss: true
                    }
                ],
                ...config
            });
        }

        /**
         * 수정 폼 모달 표시
         * @param {string} title - 모달 제목
         * @param {string} formHtml - 폼 HTML
         * @param {Function} onSave - 저장 콜백 함수
         * @param {Object} options - 추가 옵션
         */
        showEditModal(title, formHtml, onSave, options = {}) {
            const defaultOptions = {
                size: 'lg',
                backdrop: 'static',
                keyboard: false
            };
            
            const config = { ...defaultOptions, ...options };
            
            this.showModal('editModal', {
                title: title,
                body: formHtml,
                size: config.size,
                buttons: [
                    {
                        text: '취소',
                        class: 'btn-secondary',
                        dismiss: true
                    },
                    {
                        text: '저장',
                        class: 'btn-primary',
                        id: 'saveBtn',
                        action: onSave
                    }
                ],
                ...config
            });
        }

        /**
         * 생성 폼 모달 표시
         * @param {string} title - 모달 제목
         * @param {string} formHtml - 폼 HTML
         * @param {Function} onCreate - 생성 콜백 함수
         * @param {Object} options - 추가 옵션
         */
        showCreateModal(title, formHtml, onCreate, options = {}) {
            const defaultOptions = {
                size: 'lg',
                backdrop: 'static',
                keyboard: false
            };
            
            const config = { ...defaultOptions, ...options };
            
            this.showModal('createModal', {
                title: title,
                body: formHtml,
                size: config.size,
                buttons: [
                    {
                        text: '취소',
                        class: 'btn-secondary',
                        dismiss: true
                    },
                    {
                        text: '생성',
                        class: 'btn-success',
                        id: 'createBtn',
                        action: onCreate
                    }
                ],
                ...config
            });
        }

        /**
         * 삭제 확인 모달 표시
         * @param {string} message - 확인 메시지
         * @param {Function} onDelete - 삭제 콜백 함수
         * @param {Object} options - 추가 옵션
         */
        showDeleteModal(message, onDelete, options = {}) {
            const defaultOptions = {
                size: 'md',
                backdrop: true,
                keyboard: true
            };
            
            const config = { ...defaultOptions, ...options };
            
            this.showModal('deleteModal', {
                title: '삭제 확인',
                body: `
                    <div class="text-center">
                        <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
                        <p class="mb-0">${message}</p>
                        <small class="text-muted">이 작업은 되돌릴 수 없습니다.</small>
                    </div>
                `,
                size: config.size,
                buttons: [
                    {
                        text: '취소',
                        class: 'btn-secondary',
                        dismiss: true
                    },
                    {
                        text: '삭제',
                        class: 'btn-danger',
                        id: 'deleteBtn',
                        action: onDelete
                    }
                ],
                ...config
            });
        }

        /**
         * 커스텀 모달 표시
         * @param {string} title - 모달 제목
         * @param {string} content - 모달 내용
         * @param {Array} buttons - 버튼 배열
         * @param {Object} options - 추가 옵션
         */
        showCustomModal(title, content, buttons = [], options = {}) {
            const defaultOptions = {
                size: 'md',
                backdrop: true,
                keyboard: true
            };
            
            const config = { ...defaultOptions, ...options };
            
            // 기본 버튼이 없으면 닫기 버튼 추가
            if (buttons.length === 0) {
                buttons = [
                    {
                        text: '닫기',
                        class: 'btn-secondary',
                        dismiss: true
                    }
                ];
            }
            
            this.showModal('customModal', {
                title: title,
                body: content,
                size: config.size,
                buttons: buttons,
                ...config
            });
        }

        /**
         * 로딩 모달 표시
         * @param {string} message - 로딩 메시지
         * @param {Object} options - 추가 옵션
         */
        showLoadingModal(message = '처리 중...', options = {}) {
            const defaultOptions = {
                size: 'sm',
                backdrop: 'static',
                keyboard: false
            };
            
            const config = { ...defaultOptions, ...options };
            
            this.showModal('loadingModal', {
                title: '',
                body: `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary mb-3" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mb-0">${message}</p>
                    </div>
                `,
                size: config.size,
                buttons: [],
                showHeader: false,
                ...config
            });
        }

        /**
         * 모달 숨기기
         * @param {string} modalId - 모달 ID
         */
        hideModal(modalId) {
            const modal = this.modals.get(modalId);
            if (modal) {
                modal.hide();
            }
        }

        /**
         * 기본 모달 표시 (내부용)
         * @param {string} modalId - 모달 ID
         * @param {Object} config - 모달 설정
         */
        showModal(modalId, config) {
            // 기존 모달 제거
            this.cleanup(modalId);
            
            // 모달 HTML 생성
            const modalHtml = this.generateModalHtml(modalId, config);
            
            // DOM에 추가
            $('body').append(modalHtml);
            
            // 모달 초기화
            const $modal = $(`#${modalId}`);
            const modal = new bootstrap.Modal($modal[0], {
                backdrop: config.backdrop || true,
                keyboard: config.keyboard !== false,
                focus: config.focus !== false
            });
            
            // 버튼 이벤트 바인딩
            if (config.buttons) {
                config.buttons.forEach(button => {
                    if (button.action) {
                        $modal.find(`#${button.id}`).on('click', button.action);
                    }
                });
            }
            
            // 모달 저장
            this.modals.set(modalId, modal);
            
            // 모달 표시
            modal.show();
            
            return modal;
        }

        /**
         * 모달 HTML 생성
         * @param {string} modalId - 모달 ID
         * @param {Object} config - 모달 설정
         * @returns {string} 모달 HTML
         */
        generateModalHtml(modalId, config) {
            const sizeClass = config.size ? `modal-${config.size}` : '';
            const showHeader = config.showHeader !== false;
            
            let buttonsHtml = '';
            if (config.buttons && config.buttons.length > 0) {
                buttonsHtml = config.buttons.map(button => {
                    const idAttr = button.id ? `id="${button.id}"` : '';
                    const dismissAttr = button.dismiss ? 'data-bs-dismiss="modal"' : '';
                    
                    return `<button type="button" class="btn ${button.class}" ${idAttr} ${dismissAttr}>
                        ${button.text}
                    </button>`;
                }).join(' ');
            }
            
            return `
                <div class="modal fade" id="${modalId}" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog ${sizeClass}">
                        <div class="modal-content">
                            ${showHeader ? `
                                <div class="modal-header">
                                    <h5 class="modal-title">${config.title || ''}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                            ` : ''}
                            <div class="modal-body">
                                ${config.body || ''}
                            </div>
                            ${buttonsHtml ? `
                                <div class="modal-footer">
                                    ${buttonsHtml}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }

        /**
         * 객체를 테이블 형태로 렌더링
         * @param {Object} obj - 렌더링할 객체
         * @returns {string} 테이블 HTML
         */
        renderObjectAsTable(obj) {
            if (!obj || typeof obj !== 'object') {
                return '<p class="text-muted">표시할 데이터가 없습니다.</p>';
            }
            
            let html = '<div class="table-responsive"><table class="table table-bordered">';
            
            for (const [key, value] of Object.entries(obj)) {
                let displayValue = value;
                
                // 값 타입별 처리
                if (value === null || value === undefined) {
                    displayValue = '<span class="text-muted">-</span>';
                } else if (typeof value === 'boolean') {
                    displayValue = value ? '<span class="text-success">예</span>' : '<span class="text-danger">아니오</span>';
                } else if (typeof value === 'object') {
                    displayValue = '<code>' + JSON.stringify(value, null, 2) + '</code>';
                } else if (typeof value === 'string' && value.startsWith('http')) {
                    displayValue = `<a href="${value}" target="_blank">${value}</a>`;
                }
                
                html += `
                    <tr>
                        <td class="fw-bold" style="width: 30%;">${key}</td>
                        <td>${displayValue}</td>
                    </tr>
                `;
            }
            
            html += '</table></div>';
            return html;
        }

        /**
         * 모달 정리
         * @param {string} modalId - 모달 ID
         */
        cleanup(modalId) {
            // 기존 모달 제거
            const existingModal = this.modals.get(modalId);
            if (existingModal) {
                existingModal.dispose();
                this.modals.delete(modalId);
            }
            
            // DOM에서 제거
            $(`#${modalId}`).remove();
        }

        /**
         * 모든 모달 정리
         */
        cleanupAll() {
            this.modals.forEach((modal, modalId) => {
                this.cleanup(modalId);
            });
        }
    }

    // 전역 인스턴스 생성
    window.modalManager = new ModalManager();

    // jQuery 플러그인으로 등록
    $.fn.showDetailModal = function(title, content, options) {
        window.modalManager.showDetailModal(title, content, options);
        return this;
    };

    $.fn.showEditModal = function(title, formHtml, onSave, options) {
        window.modalManager.showEditModal(title, formHtml, onSave, options);
        return this;
    };

    $.fn.showCreateModal = function(title, formHtml, onCreate, options) {
        window.modalManager.showCreateModal(title, formHtml, onCreate, options);
        return this;
    };

    $.fn.showDeleteModal = function(message, onDelete, options) {
        window.modalManager.showDeleteModal(message, onDelete, options);
        return this;
    };

    $.fn.showCustomModal = function(title, content, buttons, options) {
        window.modalManager.showCustomModal(title, content, buttons, options);
        return this;
    };

    // 전역 함수로도 사용 가능
    window.showDetailModal = function(title, content, options) {
        window.modalManager.showDetailModal(title, content, options);
    };

    window.showEditModal = function(title, formHtml, onSave, options) {
        window.modalManager.showEditModal(title, formHtml, onSave, options);
    };

    window.showCreateModal = function(title, formHtml, onCreate, options) {
        window.modalManager.showCreateModal(title, formHtml, onCreate, options);
    };

    window.showDeleteModal = function(message, onDelete, options) {
        window.modalManager.showDeleteModal(message, onDelete, options);
    };

    window.showCustomModal = function(title, content, buttons, options) {
        window.modalManager.showCustomModal(title, content, buttons, options);
    };

    window.showLoadingModal = function(message, options) {
        window.modalManager.showLoadingModal(message, options);
    };

    window.hideModal = function(modalId) {
        window.modalManager.hideModal(modalId);
    };

    console.log('Racing System 모달 시스템 초기화 완료');

})(jQuery);
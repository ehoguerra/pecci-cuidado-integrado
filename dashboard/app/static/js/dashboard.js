// Dashboard Psicologia - Custom JavaScript

// Namespace para evitar conflitos
const DashboardPsi = {
    // Configurações globais
    config: {
        animationDuration: 300,
        toastDuration: 5000,
        searchDelay: 300
    },

    // Inicialização
    init: function() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupAnimations();
    },

    // Event Listeners
    setupEventListeners: function() {
        // Busca com debounce
        this.setupSearchWithDebounce();
        
        // Tooltips do Bootstrap
        this.initializeTooltips();
        
        // Confirmações de exclusão
        this.setupDeleteConfirmations();
        
        // Auto-save para formulários
        this.setupAutoSave();
        
        // Atalhos de teclado
        this.setupKeyboardShortcuts();
    },

    // Componentes
    initializeComponents: function() {
        // Máscaras para inputs
        this.setupInputMasks();
        
        // Validação em tempo real
        this.setupRealTimeValidation();
        
        // Charts se existirem
        this.initializeCharts();
    },

    // Animações
    setupAnimations: function() {
        // Animação de entrada para cards
        this.animateCards();
        
        // Loading states
        this.setupLoadingStates();
    },

    // Busca com debounce
    setupSearchWithDebounce: function() {
        const searchInputs = document.querySelectorAll('.search-input, #searchPatients, #searchEvolucoes');
        
        searchInputs.forEach(input => {
            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.performSearch(e.target);
                }, this.config.searchDelay);
            });
        });
    },

    // Realizar busca
    performSearch: function(input) {
        const searchTerm = input.value.toLowerCase();
        const targetContainer = input.dataset.target || input.getAttribute('data-target');
        
        if (input.id === 'searchPatients') {
            this.searchPatients(searchTerm);
        } else if (input.id === 'searchEvolucoes') {
            this.searchEvolucoes(searchTerm);
        }
    },

    // Busca de pacientes
    searchPatients: function(searchTerm) {
        const patientItems = document.querySelectorAll('.patient-item');
        let visibleCount = 0;
        
        patientItems.forEach(item => {
            const patientName = item.getAttribute('data-name') || '';
            const patientCard = item.querySelector('.card-title')?.textContent.toLowerCase() || '';
            
            if (patientName.includes(searchTerm) || patientCard.includes(searchTerm)) {
                item.style.display = 'block';
                item.classList.add('fade-in');
                visibleCount++;
            } else {
                item.style.display = 'none';
                item.classList.remove('fade-in');
            }
        });

        // Mostrar mensagem se nenhum resultado
        this.toggleNoResultsMessage('patients', visibleCount === 0 && searchTerm.length > 0);
    },

    // Busca de evoluções
    searchEvolucoes: function(searchTerm) {
        const evolucaoItems = document.querySelectorAll('.evolution-item');
        let visibleCount = 0;
        
        evolucaoItems.forEach(item => {
            const content = item.querySelector('.evolution-content p')?.textContent.toLowerCase() || '';
            const date = item.querySelector('.evolution-date')?.textContent.toLowerCase() || '';
            
            if (content.includes(searchTerm) || date.includes(searchTerm)) {
                item.style.display = 'block';
                item.classList.add('fade-in');
                visibleCount++;
            } else {
                item.style.display = 'none';
                item.classList.remove('fade-in');
            }
        });

        this.toggleNoResultsMessage('evolucoes', visibleCount === 0 && searchTerm.length > 0);
    },

    // Mostrar/ocultar mensagem de "nenhum resultado"
    toggleNoResultsMessage: function(type, show) {
        let messageElement = document.getElementById(`no-results-${type}`);
        
        if (show && !messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = `no-results-${type}`;
            messageElement.className = 'text-center py-4 text-muted';
            messageElement.innerHTML = `
                <i class="bi bi-search" style="font-size: 2rem;"></i>
                <p class="mt-2">Nenhum resultado encontrado</p>
            `;
            
            const container = type === 'patients' ? 
                document.getElementById('patientsContainer') : 
                document.getElementById('evolucoesList');
            
            if (container) {
                container.appendChild(messageElement);
            }
        } else if (!show && messageElement) {
            messageElement.remove();
        }
    },

    // Tooltips
    initializeTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Confirmações de exclusão
    setupDeleteConfirmations: function() {
        const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const message = button.getAttribute('data-confirm-delete') || 'Tem certeza que deseja excluir?';
                
                if (confirm(message)) {
                    // Proceder com a exclusão
                    window.location.href = button.href;
                }
            });
        });
    },

    // Auto-save para formulários
    setupAutoSave: function() {
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        
        autoSaveForms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.autoSaveForm(form, input);
                });
            });
        });
    },

    // Executar auto-save
    autoSaveForm: function(form, changedInput) {
        // Implementar lógica de auto-save
        const formData = new FormData(form);
        
        // Mostrar indicador de salvamento
        this.showSaveIndicator(changedInput, 'saving');
        
        // Simular salvamento (implementar com AJAX)
        setTimeout(() => {
            this.showSaveIndicator(changedInput, 'saved');
        }, 1000);
    },

    // Indicador de salvamento
    showSaveIndicator: function(element, status) {
        // Remover indicadores existentes
        const existingIndicator = element.parentNode.querySelector('.save-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Criar novo indicador
        const indicator = document.createElement('span');
        indicator.className = 'save-indicator small';
        
        if (status === 'saving') {
            indicator.innerHTML = '<i class="bi bi-clock text-warning"></i> Salvando...';
        } else if (status === 'saved') {
            indicator.innerHTML = '<i class="bi bi-check-circle text-success"></i> Salvo';
            
            // Remover após 2 segundos
            setTimeout(() => {
                indicator.remove();
            }, 2000);
        }
        
        element.parentNode.appendChild(indicator);
    },

    // Atalhos de teclado
    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + N = Novo paciente
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                const novoPacienteLink = document.querySelector('a[href*="novo_paciente"]');
                if (novoPacienteLink) {
                    window.location.href = novoPacienteLink.href;
                }
            }
            
            // Ctrl/Cmd + / = Focar na busca
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                const searchInput = document.querySelector('#searchPatients, #searchEvolucoes');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // ESC = Fechar modais
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal.show');
                openModals.forEach(modal => {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                });
            }
        });
    },

    // Máscaras para inputs
    setupInputMasks: function() {
        // Máscara para CRP
        const crpInputs = document.querySelectorAll('input[name*="crp"]');
        crpInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 0) {
                    value = value.replace(/(\d{2})(\d{0,6})/, '$1/$2');
                }
                e.target.value = value;
            });
        });

        // Máscara para telefone
        const phoneInputs = document.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 11) {
                    value = value.replace(/(\d{2})(\d{0,5})(\d{0,4})/, '($1) $2-$3');
                }
                e.target.value = value;
            });
        });
    },

    // Validação em tempo real
    setupRealTimeValidation: function() {
        const requiredInputs = document.querySelectorAll('input[required], textarea[required]');
        
        requiredInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateInput(input);
            });
            
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateInput(input);
                }
            });
        });
    },

    // Validar input individual
    validateInput: function(input) {
        const value = input.value.trim();
        const isValid = input.checkValidity();
        
        input.classList.remove('is-valid', 'is-invalid');
        
        if (value.length > 0) {
            input.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }
        
        return isValid;
    },

    // Animação de cards
    animateCards: function() {
        const cards = document.querySelectorAll('.card:not(.no-animation)');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1
        });
        
        cards.forEach(card => {
            observer.observe(card);
        });
    },

    // Loading states
    setupLoadingStates: function() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                
                if (submitButton) {
                    submitButton.disabled = true;
                    
                    const originalText = submitButton.textContent;
                    submitButton.innerHTML = '<span class="loading"></span> Processando...';
                    
                    // Restaurar após timeout (caso não haja redirecionamento)
                    setTimeout(() => {
                        submitButton.disabled = false;
                        submitButton.textContent = originalText;
                    }, 5000);
                }
            });
        });
    },

    // Charts (se necessário)
    initializeCharts: function() {
        // Implementar charts com Chart.js ou similar se necessário
        console.log('Charts initialized');
    },

    // Notificações toast
    showToast: function(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} align-items-center border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            delay: this.config.toastDuration
        });
        
        bsToast.show();
        
        // Remover do DOM após ocultação
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Criar container de toasts
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1080';
        
        document.body.appendChild(container);
        return container;
    },

    // Utilitários
    utils: {
        // Formatar data
        formatDate: function(date) {
            return new Date(date).toLocaleDateString('pt-BR');
        },
        
        // Calcular idade
        calculateAge: function(birthDate) {
            const today = new Date();
            const birth = new Date(birthDate);
            let age = today.getFullYear() - birth.getFullYear();
            const monthDiff = today.getMonth() - birth.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
                age--;
            }
            
            return age;
        },
        
        // Debounce function
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
        }
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    DashboardPsi.init();
});

// Exportar para uso global se necessário
window.DashboardPsi = DashboardPsi;

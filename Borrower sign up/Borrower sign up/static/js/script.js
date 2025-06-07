// Professional JavaScript for Loan Application
class LoanApplication {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 3;
        this.formData = {};
        this.validationRules = this.initValidationRules();
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.initFormValidation();
        this.initLoanCalculator();
        this.initFlashMessages();
        this.initMobileMenu();
    }
    
    bindEvents() {
        // Step navigation
        document.querySelectorAll('.next-step').forEach(btn => {
            btn.addEventListener('click', () => this.nextStep());
        });
        
        document.querySelectorAll('.prev-step').forEach(btn => {
            btn.addEventListener('click', () => this.prevStep());
        });
        
        // Form submission
        const form = document.getElementById('borrowerForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        // Real-time validation
        document.querySelectorAll('input, select').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearFieldError(field));
        });
        
        // Loan amount to words conversion
        const loanAmountField = document.getElementById('loan_amount');
        if (loanAmountField) {
            loanAmountField.addEventListener('input', () => this.updateAmountWords());
        }
        
        // Employment status change
        const employmentField = document.getElementById('employment_status');
        if (employmentField) {
            employmentField.addEventListener('change', () => this.handleEmploymentChange());
        }
    }
    
    initValidationRules() {
        return {
            first_name: {
                required: true,
                minLength: 2,
                pattern: /^[a-zA-Z\s]+$/,
                message: 'First name must contain only letters and be at least 2 characters'
            },
            last_name: {
                required: true,
                minLength: 2,
                pattern: /^[a-zA-Z\s]+$/,
                message: 'Last name must contain only letters and be at least 2 characters'
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Please enter a valid email address'
            },
            phone: {
                required: true,
                pattern: /^[6-9]\d{9}$/,
                message: 'Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9'
            },
            date_of_birth: {
                required: true,
                custom: (value) => {
                    const today = new Date();
                    const birthDate = new Date(value);
                    const age = today.getFullYear() - birthDate.getFullYear();
                    return age >= 18 && age <= 80;
                },
                message: 'You must be between 18 and 80 years old'
            },
            address: {
                required: true,
                minLength: 10,
                message: 'Please enter a complete address (minimum 10 characters)'
            },
            city: {
                required: true,
                minLength: 2,
                pattern: /^[a-zA-Z\s]+$/,
                message: 'City name must contain only letters'
            },
            state: {
                required: true,
                message: 'Please select your state'
            },
            zip_code: {
                required: true,
                pattern: /^\d{6}$/,
                message: 'Please enter a valid 6-digit PIN code'
            },
            employment_status: {
                required: true,
                message: 'Please select your employment status'
            },
            annual_income: {
                required: false,
                min: 0,
                message: 'Annual income must be a positive number'
            },
            loan_amount: {
                required: true,
                min: 10000,
                max: 10000000,
                message: 'Loan amount must be between ₹10,000 and ₹1,00,00,000'
            },
            loan_purpose: {
                required: true,
                message: 'Please select the purpose of your loan'
            }
        };
    }
    
    validateField(field) {
        const fieldName = field.name;
        const value = field.value.trim();
        const rules = this.validationRules[fieldName];
        
        if (!rules) return true;
        
        // Clear previous errors
        this.clearFieldError(field);
        
        // Required validation
        if (rules.required && !value) {
            this.showFieldError(field, `${this.getFieldLabel(fieldName)} is required`);
            return false;
        }
        
        // Skip other validations if field is empty and not required
        if (!value && !rules.required) return true;
        
        // Pattern validation
        if (rules.pattern && !rules.pattern.test(value)) {
            this.showFieldError(field, rules.message);
            return false;
        }
        
        // Length validation
        if (rules.minLength && value.length < rules.minLength) {
            this.showFieldError(field, rules.message);
            return false;
        }
        
        // Number validation
        if (rules.min !== undefined) {
            const numValue = parseFloat(value);
            if (isNaN(numValue) || numValue < rules.min) {
                this.showFieldError(field, rules.message);
                return false;
            }
        }
        
        if (rules.max !== undefined) {
            const numValue = parseFloat(value);
            if (numValue > rules.max) {
                this.showFieldError(field, rules.message);
                return false;
            }
        }
        
        // Custom validation
        if (rules.custom && !rules.custom(value)) {
            this.showFieldError(field, rules.message);
            return false;
        }
        
        // Mark field as valid
        this.markFieldValid(field);
        return true;
    }
    
    showFieldError(field, message) {
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        formGroup.classList.add('has-error');
        formGroup.classList.remove('has-success');
        
        if (errorElement) {
            errorElement.textContent = message;
        }
        
        // Add shake animation
        field.classList.add('shake');
        setTimeout(() => field.classList.remove('shake'), 500);
    }
    
    clearFieldError(field) {
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        formGroup.classList.remove('has-error');
        
        if (errorElement) {
            errorElement.textContent = '';
        }
    }
    
    markFieldValid(field) {
        const formGroup = field.closest('.form-group');
        formGroup.classList.add('has-success');
        formGroup.classList.remove('has-error');
    }
    
    getFieldLabel(fieldName) {
        const labelMap = {
            first_name: 'First Name',
            last_name: 'Last Name',
            email: 'Email Address',
            phone: 'Phone Number',
            date_of_birth: 'Date of Birth',
            address: 'Address',
            city: 'City',
            state: 'State',
            zip_code: 'PIN Code',
            employment_status: 'Employment Status',
            annual_income: 'Annual Income',
            loan_amount: 'Loan Amount',
            loan_purpose: 'Loan Purpose'
        };
        return labelMap[fieldName] || fieldName;
    }
    
    validateStep(stepNumber) {
        const stepFields = this.getStepFields(stepNumber);
        let isValid = true;
        
        stepFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    getStepFields(stepNumber) {
        const stepFieldMap = {
            1: ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'city', 'state', 'zip_code'],
            2: ['employment_status', 'annual_income'],
            3: ['loan_amount', 'loan_purpose']
        };
        
        return stepFieldMap[stepNumber]?.map(name => 
            document.querySelector(`[name="${name}"]`)
        ).filter(field => field) || [];
    }
    
    nextStep() {
        if (this.validateStep(this.currentStep)) {
            if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.updateStepDisplay();
                this.scrollToTop();
            }
        } else {
            this.showMessage('Please correct the errors before proceeding', 'error');
        }
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
            this.scrollToTop();
        }
    }
    
    updateStepDisplay() {
        // Update progress steps
        document.querySelectorAll('.step').forEach((step, index) => {
            if (index + 1 === this.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        // Update form steps
        document.querySelectorAll('.form-step').forEach((step, index) => {
            if (index + 1 === this.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        // Update progress bar if exists
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const progress = (this.currentStep / this.totalSteps) * 100;
            progressBar.style.width = `${progress}%`;
        }
    }
    
    scrollToTop() {
        document.querySelector('.application-section').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
    
    initLoanCalculator() {
        const loanAmountField = document.getElementById('loan_amount');
        const loanPurposeField = document.getElementById('loan_purpose');
        
        if (loanAmountField) {
            loanAmountField.addEventListener('input', () => this.calculateLoan());
        }
        
        if (loanPurposeField) {
            loanPurposeField.addEventListener('change', () => this.calculateLoan());
        }
        
        // Initial calculation
        this.calculateLoan();
    }
    
    calculateLoan() {
        const loanAmount = parseFloat(document.getElementById('loan_amount')?.value) || 0;
        const loanPurpose = document.getElementById('loan_purpose')?.value || '';
        
        if (loanAmount <= 0) {
            this.updateCalculatorDisplay(0, 0, 0);
            return;
        }
        
        // Interest rates based on loan purpose
        const interestRates = {
            home_loan: 8.5,
            car_loan: 9.5,
            personal_loan: 12.5,
            business_loan: 11.0,
            education_loan: 10.0,
            gold_loan: 7.5,
            default: 12.5
        };
        
        const interestRate = interestRates[loanPurpose] || interestRates.default;
        const tenure = this.getDefaultTenure(loanPurpose); // in months
        const monthlyRate = interestRate / 12 / 100;
        
        // EMI calculation using formula: P * r * (1+r)^n / ((1+r)^n - 1)
        let emi = 0;
        if (monthlyRate > 0) {
            const factor = Math.pow(1 + monthlyRate, tenure);
            emi = (loanAmount * monthlyRate * factor) / (factor - 1);
        } else {
            emi = loanAmount / tenure;
        }
        
        // Processing fee calculation (typically 1-2% of loan amount)
        const processingFee = Math.min(loanAmount * 0.015, 50000); // 1.5% or max ₹50,000
        
        this.updateCalculatorDisplay(emi, interestRate, processingFee);
    }
    
    getDefaultTenure(loanPurpose) {
        const tenureMap = {
            home_loan: 240, // 20 years
            car_loan: 60,   // 5 years
            personal_loan: 36, // 3 years
            business_loan: 60, // 5 years
            education_loan: 84, // 7 years
            gold_loan: 12,  // 1 year
            default: 36     // 3 years
        };
        return tenureMap[loanPurpose] || tenureMap.default;
    }
    
    updateCalculatorDisplay(emi, interestRate, processingFee) {
        const emiElement = document.getElementById('estimated-emi');
        const rateElement = document.getElementById('interest-rate');
        const feeElement = document.getElementById('processing-fee');
        
        if (emiElement) {
            emiElement.textContent = `₹${this.formatNumber(Math.round(emi))}`;
        }
        
        if (rateElement) {
            rateElement.textContent = `${interestRate}% p.a.`;
        }
        
        if (feeElement) {
            feeElement.textContent = `₹${this.formatNumber(Math.round(processingFee))}`;
        }
    }
    
    updateAmountWords() {
        const loanAmount = parseFloat(document.getElementById('loan_amount')?.value) || 0;
        const wordsElement = document.getElementById('loan_amount_words');
        
        if (wordsElement && loanAmount > 0) {
            wordsElement.textContent = `In words: ${this.numberToWords(loanAmount)} Rupees Only`;
        } else if (wordsElement) {
            wordsElement.textContent = '';
        }
    }
    
    numberToWords(num) {
        if (num === 0) return 'Zero';
        
        const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
        const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
        const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
        const thousands = ['', 'Thousand', 'Lakh', 'Crore'];
        
        function convertHundreds(n) {
            let result = '';
            if (n >= 100) {
                result += ones[Math.floor(n / 100)] + ' Hundred ';
                n %= 100;
            }
            if (n >= 20) {
                result += tens[Math.floor(n / 10)] + ' ';
                n %= 10;
            } else if (n >= 10) {
                result += teens[n - 10] + ' ';
                return result;
            }
            if (n > 0) {
                result += ones[n] + ' ';
            }
            return result;
        }
        
        let result = '';
        let thousandCounter = 0;
        
        while (num > 0) {
            if (num % 1000 !== 0) {
                result = convertHundreds(num % 1000) + thousands[thousandCounter] + ' ' + result;
            }
            num = Math.floor(num / 1000);
            thousandCounter++;
        }
        
        return result.trim();
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat('en-IN').format(num);
    }
    
    handleEmploymentChange() {
        const employmentStatus = document.getElementById('employment_status')?.value;
        const incomeField = document.getElementById('annual_income');
        const incomeGroup = incomeField?.closest('.form-group');
        
        if (employmentStatus === 'unemployed' || employmentStatus === 'student') {
            incomeGroup?.classList.add('optional');
            if (incomeField) {
                incomeField.required = false;
            }
        } else {
            incomeGroup?.classList.remove('optional');
            if (incomeField) {
                incomeField.required = true;
            }
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        // Validate all steps
        let isFormValid = true;
        for (let step = 1; step <= this.totalSteps; step++) {
            if (!this.validateStep(step)) {
                isFormValid = false;
                this.currentStep = step;
                this.updateStepDisplay();
                break;
            }
        }
        
        if (!isFormValid) {
            this.showMessage('Please correct all errors before submitting', 'error');
            return;
        }
        
        // Show loading state
        this.showLoading(true);
        const submitBtn = document.getElementById('submitBtn');
        this.setButtonLoading(submitBtn, true);
        
        try {
            const formData = new FormData(e.target);
            const response = await fetch('/apply', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage('Application submitted successfully! We will contact you soon.', 'success');
                this.resetForm();
            } else {
                this.showMessage(result.message || 'An error occurred. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Submission error:', error);
            this.showMessage('Network error. Please check your connection and try again.', 'error');
        } finally {
            this.showLoading(false);
            this.setButtonLoading(submitBtn, false);
        }
    }
    
    showLoading(show) {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.toggle('show', show);
        }
    }
    
    setButtonLoading(button, loading) {
        if (!button) return;
        
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (loading) {
            button.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnLoading) btnLoading.style.display = 'inline-flex';
        } else {
            button.disabled = false;
            if (btnText) btnText.style.display = 'inline';
            if (btnLoading) btnLoading.style.display = 'none';
        }
    }
    
    resetForm() {
        document.getElementById('borrowerForm')?.reset();
        this.currentStep = 1;
        this.updateStepDisplay();
        
        // Clear all validation states
        document.querySelectorAll('.form-group').forEach(group => {
            group.classList.remove('has-error', 'has-success');
        });
        
        document.querySelectorAll('.error-message').forEach(error => {
            error.textContent = '';
        });
        
        // Reset calculator
        this.updateCalculatorDisplay(0, 12.5, 0);
        this.updateAmountWords();
    }
    
    initFlashMessages() {
        // Auto-hide flash messages after 5 seconds
        document.querySelectorAll('.flash-message').forEach(message => {
            setTimeout(() => {
                message.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
        
        // Close button functionality
        document.querySelectorAll('.flash-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.closest('.flash-message');
                message.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => message.remove(), 300);
            });
        });
    }
    
    showMessage(text, type = 'info') {
        const container = document.querySelector('.flash-messages') || this.createFlashContainer();
        
        const message = document.createElement('div');
        message.className = `flash-message flash-${type}`;
        message.innerHTML = `
            <i class="fas fa-${this.getMessageIcon(type)}"></i>
            <span>${text}</span>
            <button class="flash-close" type="button">&times;</button>
        `;
        
        container.appendChild(message);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            message.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => message.remove(), 300);
        }, 5000);
        
        // Close button functionality
        message.querySelector('.flash-close').addEventListener('click', () => {
            message.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => message.remove(), 300);
        });
    }
    
    createFlashContainer() {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
        return container;
    }
    
    getMessageIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }
    
    initMobileMenu() {
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                }
            });
        }
    }
    
    initFormValidation() {
        // Add shake animation CSS if not exists
        if (!document.querySelector('#shake-animation')) {
            const style = document.createElement('style');
            style.id = 'shake-animation';
            style.textContent = `
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                    20%, 40%, 60%, 80% { transform: translateX(5px); }
                }
                .shake { animation: shake 0.5s ease-in-out; }
                @keyframes slideOutRight {
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Utility Functions
class LoanUtils {
    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }
    
    static formatDate(date) {
        return new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }
    
    static debounce(func, wait) {
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
    
    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    static validatePAN(pan) {
        const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
        return panRegex.test(pan);
    }
    
    static validateAadhaar(aadhaar) {
        const aadhaarRegex = /^\d{12}$/;
        return aadhaarRegex.test(aadhaar.replace(/\s/g, ''));
    }
    
    static calculateAge(birthDate) {
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    }
    
    static generateApplicationId() {
        const timestamp = Date.now().toString(36);
        const randomStr = Math.random().toString(36).substr(2, 5);
        return `LP${timestamp}${randomStr}`.toUpperCase();
    }
}

// Enhanced Form Validation
class FormValidator {
    constructor() {
        this.rules = new Map();
        this.customValidators = new Map();
        this.initCustomValidators();
    }
    
    initCustomValidators() {
        this.customValidators.set('pan', (value) => {
            return LoanUtils.validatePAN(value);
        });
        
        this.customValidators.set('aadhaar', (value) => {
            return LoanUtils.validateAadhaar(value);
        });
        
        this.customValidators.set('ifsc', (value) => {
            const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/;
            return ifscRegex.test(value);
        });
        
        this.customValidators.set('age', (value) => {
            const age = LoanUtils.calculateAge(value);
            return age >= 18 && age <= 80;
        });
    }
    
    addRule(fieldName, rule) {
        if (!this.rules.has(fieldName)) {
            this.rules.set(fieldName, []);
        }
        this.rules.get(fieldName).push(rule);
    }
    
    validate(fieldName, value) {
        const fieldRules = this.rules.get(fieldName) || [];
        
        for (const rule of fieldRules) {
            const result = this.executeRule(rule, value);
            if (!result.isValid) {
                return result;
            }
        }
        
        return { isValid: true };
    }
    
    executeRule(rule, value) {
        switch (rule.type) {
            case 'required':
                return {
                    isValid: value && value.trim().length > 0,
                    message: rule.message || 'This field is required'
                };
            
            case 'minLength':
                return {
                    isValid: value.length >= rule.value,
                    message: rule.message || `Minimum ${rule.value} characters required`
                };
            
            case 'maxLength':
                return {
                    isValid: value.length <= rule.value,
                    message: rule.message || `Maximum ${rule.value} characters allowed`
                };
            
            case 'pattern':
                return {
                    isValid: rule.value.test(value),
                    message: rule.message || 'Invalid format'
                };
            
            case 'custom':
                const validator = this.customValidators.get(rule.validator);
                return {
                    isValid: validator ? validator(value) : true,
                    message: rule.message || 'Invalid value'
                };
            
            default:
                return { isValid: true };
        }
    }
}

// Analytics and Tracking
class LoanAnalytics {
    constructor() {
        this.events = [];
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    track(eventName, properties = {}) {
        const event = {
            name: eventName,
            properties: {
                ...properties,
                sessionId: this.sessionId,
                timestamp: Date.now(),
                url: window.location.href,
                userAgent: navigator.userAgent
            }
        };
        
        this.events.push(event);
        
        // Send to analytics service (implement as needed)
        this.sendToAnalytics(event);
    }
    
    sendToAnalytics(event) {
        // Implement analytics service integration
        console.log('Analytics Event:', event);
        
        // Example: Send to Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', event.name, event.properties);
        }
    }
    
    trackFormStep(stepNumber) {
        this.track('form_step_viewed', {
            step: stepNumber,
            stepName: this.getStepName(stepNumber)
        });
    }
    
    trackFormSubmission(success, errorMessage = null) {
        this.track('form_submitted', {
            success: success,
            errorMessage: errorMessage,
            timeSpent: Date.now() - this.startTime
        });
    }
    
    trackFieldInteraction(fieldName, action) {
        this.track('field_interaction', {
            fieldName: fieldName,
            action: action
        });
    }
    
    getStepName(stepNumber) {
        const stepNames = {
            1: 'Personal Information',
            2: 'Employment Details',
            3: 'Loan Information'
        };
        return stepNames[stepNumber] || `Step ${stepNumber}`;
    }
}

// Performance Monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }
    
    init() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            this.recordPageLoadMetrics();
        });
        
        // Monitor form performance
        this.monitorFormPerformance();
    }
    
    recordPageLoadMetrics() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            
            this.metrics.pageLoad = {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                totalTime: navigation.loadEventEnd - navigation.fetchStart
            };
            
            console.log('Page Load Metrics:', this.metrics.pageLoad);
        }
    }
    
    monitorFormPerformance() {
        const formStartTime = Date.now();
        
        document.addEventListener('DOMContentLoaded', () => {
            this.metrics.formRenderTime = Date.now() - formStartTime;
        });
    }
    
    measureFunction(name, fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        
        this.metrics[name] = end - start;
        console.log(`${name} took ${end - start} milliseconds`);
        
        return result;
    }
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main application
    window.loanApp = new LoanApplication();
    
    // Initialize analytics
    window.analytics = new LoanAnalytics();
    
    // Initialize performance monitoring
    window.performanceMonitor = new PerformanceMonitor();
    
    // Track initial page view
    window.analytics.track('page_viewed', {
        page: 'loan_application',
        referrer: document.referrer
    });
    
    // Add global error handling
    window.addEventListener('error', (e) => {
        console.error('Global error:', e.error);
        window.analytics.track('javascript_error', {
            message: e.message,
            filename: e.filename,
            lineno: e.lineno,
            colno: e.colno
        });
    });
    
    // Add unhandled promise rejection handling
    window.addEventListener('unhandledrejection', (e) => {
        console.error('Unhandled promise rejection:', e.reason);
        window.analytics.track('promise_rejection', {
            reason: e.reason.toString()
        });
    });
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        LoanApplication,
        LoanUtils,
        FormValidator,
        LoanAnalytics,
        PerformanceMonitor
    };
}
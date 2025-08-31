/**
 * Main JavaScript for Snowsports Program Manager
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // File input preview
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = e.target.files[0] ? e.target.files[0].name : 'Choose file';
            var label = e.target.nextElementSibling;
            label.textContent = fileName;
        });
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Dynamic form fields
    document.body.addEventListener('click', function(e) {
        // Add more form fields
        if (e.target.matches('.add-form-field')) {
            e.preventDefault();
            var container = document.querySelector(e.target.dataset.target);
            var template = container.dataset.prototype;
            var index = container.dataset.index || container.children.length;
            var newField = template.replace(/__name__/g, index);
            container.insertAdjacentHTML('beforeend', newField);
            container.dataset.index = parseInt(index) + 1;
        }

        // Remove form fields
        if (e.target.matches('.remove-form-field')) {
            e.preventDefault();
            var field = e.target.closest('.form-field-group');
            if (field) {
                field.remove();
            }
        }
    });

    // Table sorting
    document.querySelectorAll('.sortable th[data-sort]').forEach(header => {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const index = this.cellIndex;
            const isNumeric = this.classList.contains('numeric');
            const isAsc = !this.classList.contains('asc');
            
            // Reset all headers
            table.querySelectorAll('th').forEach(th => {
                th.classList.remove('asc', 'desc');
            });
            
            // Set current sort direction
            this.classList.toggle('asc', isAsc);
            this.classList.toggle('desc', !isAsc);
            
            // Sort the table
            sortTable(table, index, isAsc, isNumeric);
        });
    });
});

/**
 * Sort a table by the given column
 */
function sortTable(table, col, isAsc, isNumeric) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Sort the rows
    rows.sort((a, b) => {
        const aVal = a.cells[col].textContent.trim();
        const bVal = b.cells[col].textContent.trim();
        
        if (isNumeric) {
            return isAsc ? aVal - bVal : bVal - aVal;
        } else {
            return isAsc 
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal);
        }
    });
    
    // Remove all existing rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    // Re-add the sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Show a loading spinner
 */
function showLoading() {
    const loading = document.createElement('div');
    loading.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-dark bg-opacity-50';
    loading.style.zIndex = '9999';
    loading.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(loading);
    return loading;
}

/**
 * Hide loading spinner
 */
function hideLoading(loadingElement) {
    if (loadingElement && loadingElement.parentNode) {
        loadingElement.parentNode.removeChild(loadingElement);
    }
}

/**
 * AJAX form submission
 */
function submitForm(form, callback) {
    const formData = new FormData(form);
    const url = form.getAttribute('action') || window.location.href;
    const method = form.getAttribute('method') || 'POST';
    
    const loading = showLoading();
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(loading);
        if (typeof callback === 'function') {
            callback(data);
        }
    })
    .catch(error => {
        hideLoading(loading);
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    const toastId = 'toast-' + Date.now();
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast show align-items-center text-white bg-${type} border-0`;
    toast.role = 'alert';
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove toast after 5 seconds
    setTimeout(() => {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.hide();
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }, 5000);
}

/**
 * Create a toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

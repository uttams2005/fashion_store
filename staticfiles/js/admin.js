// Admin Dashboard JavaScript

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
    
    // Initialize modals
    var modalList = [].slice.call(document.querySelectorAll('.modal'));
    modalList.forEach(function (modalEl) {
        new bootstrap.Modal(modalEl);
    });
    
    // Sidebar navigation enhancement
    initializeSidebar();
    
    // Form validation enhancement
    initializeFormValidation();
    
    // Table enhancements
    initializeTables();
    
    // Dashboard charts (placeholder for future enhancement)
    initializeDashboardCharts();
    
    // Real-time updates
    initializeRealTimeUpdates();
    
    // Admin-specific utilities
    initializeAdminUtilities();
});

// Initialize sidebar functionality
function initializeSidebar() {
    const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
    const currentPath = window.location.pathname;
    
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href.split('/')[1])) {
            link.classList.add('active');
        }
        
        // Add click effect
        link.addEventListener('click', function() {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
        });
    }
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Validate individual field
function validateField(field) {
    const value = field.value.trim();
    const required = field.hasAttribute('required');
    const minLength = field.getAttribute('minlength');
    const maxLength = field.getAttribute('maxlength');
    const pattern = field.getAttribute('pattern');
    
    // Clear previous errors
    clearFieldError(field);
    
    // Required field validation
    if (required && !value) {
        showFieldError(field, 'This field is required.');
        return false;
    }
    
    // Length validation
    if (minLength && value.length < parseInt(minLength)) {
        showFieldError(field, `Minimum length is ${minLength} characters.`);
        return false;
    }
    
    if (maxLength && value.length > parseInt(maxLength)) {
        showFieldError(field, `Maximum length is ${maxLength} characters.`);
        return false;
    }
    
    // Pattern validation
    if (pattern && !new RegExp(pattern).test(value)) {
        showFieldError(field, 'Please enter a valid value.');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address.');
            return false;
        }
    }
    
    // Number validation
    if (field.type === 'number' && value) {
        const num = parseFloat(value);
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        
        if (isNaN(num)) {
            showFieldError(field, 'Please enter a valid number.');
            return false;
        }
        
        if (min && num < parseFloat(min)) {
            showFieldError(field, `Minimum value is ${min}.`);
            return false;
        }
        
        if (max && num > parseFloat(max)) {
            showFieldError(field, `Maximum value is ${max}.`);
            return false;
        }
    }
    
    return true;
}

// Show field error
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Validate entire form
function validateForm(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Initialize table enhancements
function initializeTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // Add sorting functionality
        addTableSorting(table);
        
        // Add search functionality
        addTableSearch(table);
        
        // Add pagination (if needed)
        addTablePagination(table);
    });
}

// Add table sorting
function addTableSorting(table) {
    const headers = table.querySelectorAll('th[data-sortable]');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const column = Array.from(this.parentNode.children).indexOf(this);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Toggle sort direction
            const isAscending = this.classList.contains('sort-asc');
            this.classList.toggle('sort-asc');
            this.classList.toggle('sort-desc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.children[column].textContent.trim();
                const bValue = b.children[column].textContent.trim();
                
                if (isAscending) {
                    return bValue.localeCompare(aValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// Add table search
function addTableSearch(table) {
    const searchContainer = table.parentNode.querySelector('.table-search');
    if (!searchContainer) return;
    
    const searchInput = searchContainer.querySelector('input');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Add table pagination
function addTablePagination(table) {
    const paginationContainer = table.parentNode.querySelector('.table-pagination');
    if (!paginationContainer) return;
    
    const rowsPerPage = 10;
    const rows = table.querySelectorAll('tbody tr');
    const totalPages = Math.ceil(rows.length / rowsPerPage);
    
    if (totalPages <= 1) return;
    
    // Create pagination controls
    const pagination = document.createElement('nav');
    pagination.innerHTML = `
        <ul class="pagination justify-content-center">
            <li class="page-item">
                <button class="page-link" data-page="prev">Previous</button>
            </li>
            <li class="page-item">
                <button class="page-link" data-page="next">Next</button>
            </li>
        </ul>
    `;
    
    paginationContainer.appendChild(pagination);
    
    // Show first page
    showTablePage(table, 1, rowsPerPage);
    
    // Handle pagination clicks
    pagination.addEventListener('click', function(e) {
        if (e.target.classList.contains('page-link')) {
            const page = e.target.dataset.page;
            const currentPage = parseInt(table.dataset.currentPage) || 1;
            
            if (page === 'prev' && currentPage > 1) {
                showTablePage(table, currentPage - 1, rowsPerPage);
            } else if (page === 'next' && currentPage < totalPages) {
                showTablePage(table, currentPage + 1, rowsPerPage);
            }
        }
    });
}

// Show specific table page
function showTablePage(table, page, rowsPerPage) {
    const rows = table.querySelectorAll('tbody tr');
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    
    rows.forEach((row, index) => {
        if (index >= start && index < end) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    table.dataset.currentPage = page;
}

// Initialize dashboard charts
function initializeDashboardCharts() {
    // Placeholder for chart initialization
    // This could include Chart.js or other charting libraries
    
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        // Initialize charts here when needed
        console.log('Chart container found:', container);
    });
}

// Initialize real-time updates
function initializeRealTimeUpdates() {
    // Placeholder for real-time functionality
    // This could include WebSocket connections for live updates
    
    // Example: Update dashboard stats every 30 seconds
    setInterval(() => {
        // Could fetch updated stats via AJAX
        console.log('Checking for updates...');
    }, 30000);
}

// Initialize admin utilities
function initializeAdminUtilities() {
    // Bulk actions
    initializeBulkActions();
    
    // Export functionality
    initializeExport();
    
    // Quick actions
    initializeQuickActions();
}

// Initialize bulk actions
function initializeBulkActions() {
    const bulkActionForms = document.querySelectorAll('.bulk-action-form');
    
    bulkActionForms.forEach(form => {
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        const bulkActionSelect = form.querySelector('.bulk-action-select');
        const bulkActionButton = form.querySelector('.bulk-action-button');
        
        if (checkboxes.length && bulkActionSelect && bulkActionButton) {
            // Update button state based on selections
            function updateBulkActionButton() {
                const checkedBoxes = form.querySelectorAll('input[type="checkbox"]:checked');
                bulkActionButton.disabled = checkedBoxes.length === 0;
            }
            
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', updateBulkActionButton);
            });
            
            // Handle bulk action submission
            bulkActionButton.addEventListener('click', function(e) {
                const action = bulkActionSelect.value;
                const checkedBoxes = form.querySelectorAll('input[type="checkbox"]:checked');
                
                if (action && checkedBoxes.length > 0) {
                    if (confirm(`Are you sure you want to ${action} ${checkedBoxes.length} item(s)?`)) {
                        // Add action to form data
                        const actionInput = document.createElement('input');
                        actionInput.type = 'hidden';
                        actionInput.name = 'bulk_action';
                        actionInput.value = action;
                        form.appendChild(actionInput);
                        
                        // Submit form
                        form.submit();
                    }
                }
            });
        }
    });
}

// Initialize export functionality
function initializeExport() {
    const exportButtons = document.querySelectorAll('.export-btn');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const format = this.dataset.format || 'csv';
            const table = this.closest('.card').querySelector('.table');
            
            if (table) {
                exportTable(table, format);
            }
        });
    });
}

// Export table data
function exportTable(table, format) {
    const rows = table.querySelectorAll('tbody tr');
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    
    let data = [headers];
    
    rows.forEach(row => {
        const rowData = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
        data.push(rowData);
    });
    
    if (format === 'csv') {
        exportCSV(data);
    } else if (format === 'json') {
        exportJSON(data);
    }
}

// Export as CSV
function exportCSV(data) {
    const csvContent = data.map(row => 
        row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Export as JSON
function exportJSON(data) {
    const headers = data[0];
    const jsonData = data.slice(1).map(row => {
        const obj = {};
        headers.forEach((header, index) => {
            obj[header] = row[index];
        });
        return obj;
    });
    
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'export.json';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize quick actions
function initializeQuickActions() {
    const quickActionButtons = document.querySelectorAll('.quick-action-btn');
    
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.dataset.action;
            
            switch (action) {
                case 'refresh':
                    window.location.reload();
                    break;
                case 'back':
                    window.history.back();
                    break;
                case 'print':
                    window.print();
                    break;
                default:
                    console.log('Quick action not implemented:', action);
            }
        });
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Export utility functions
window.AdminUtils = {
    showNotification,
    validateForm,
    exportTable
};

// Main JavaScript file for Campus Event Management

// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function () {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })
});

// File input preview for image uploads
function previewImage(input, previewElement) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    
    reader.onload = function(e) {
      document.getElementById(previewElement).src = e.target.result;
      document.getElementById(previewElement).style.display = 'block';
    }
    
    reader.readAsDataURL(input.files[0]);
  }
}

// Form validation for password match
function validatePasswordMatch(password, confirmPassword, errorElement) {
  const errorMsg = document.getElementById(errorElement);
  if (password.value !== confirmPassword.value) {
    errorMsg.textContent = 'Passwords do not match';
    errorMsg.style.display = 'block';
    return false;
  } else {
    errorMsg.style.display = 'none';
    return true;
  }
}

// Dynamic form fields validation
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;
  
  return form.checkValidity();
}

// Confirm delete actions
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this item? This action cannot be undone.');
}

// Format date and time for display
function formatDateTime(dateTimeStr, format) {
  const date = new Date(dateTimeStr);
  
  if (format === 'date') {
    return date.toLocaleDateString();
  } else if (format === 'time') {
    return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  } else {
    return date.toLocaleString();
  }
}
// Calendar.js - Handles the FullCalendar integration

document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('calendar')) {
    initializeCalendar();
  }
});

function initializeCalendar() {
  var calendarEl = document.getElementById('calendar');
  
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,listWeek'
    },
    themeSystem: 'bootstrap',
    events: '/events/calendar/data',
    eventTimeFormat: {
      hour: '2-digit',
      minute: '2-digit',
      meridiem: 'short'
    },
    eventClick: function(info) {
      window.location.href = '/events/' + info.event.id;
    },
    loading: function(isLoading) {
      if (isLoading) {
        document.getElementById('loading-indicator').style.display = 'block';
      } else {
        document.getElementById('loading-indicator').style.display = 'none';
      }
    }
  });
  
  calendar.render();
  
  // Add filter functionality
  document.querySelectorAll('.calendar-filter').forEach(function(filter) {
    filter.addEventListener('change', function() {
      updateCalendarView();
    });
  });
  
  function updateCalendarView() {
    var categoryFilter = document.getElementById('category-filter');
    var selectedCategory = categoryFilter ? categoryFilter.value : '';
    
    calendar.getEvents().forEach(function(event) {
      if (selectedCategory === '' || selectedCategory === event.extendedProps.category) {
        event.setProp('display', 'auto');
      } else {
        event.setProp('display', 'none');
      }
    });
  }
}
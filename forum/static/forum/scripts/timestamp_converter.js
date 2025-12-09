(function(){
  /**
   * Convert all UTC timestamps to local browser time
   * Looks for elements with data-utc-timestamp attribute
   * Displays them in the user's local timezone
   */
  
  function formatTimestamp(utcDateString) {
    try {
      // Parse the UTC datetime string
      const utcDate = new Date(utcDateString);
      
      if (isNaN(utcDate.getTime())) {
        return utcDateString; // Return original if parsing failed
      }
      
      // Format: "Dec 9, 2025 3:45 PM"
      const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      };
      
      return new Intl.DateTimeFormat('en-US', options).format(utcDate);
    } catch (e) {
      return utcDateString; // Return original if any error occurs
    }
  }
  
  function convertTimestamps() {
    // Find all elements with data-utc-timestamp attribute
    const timestamps = document.querySelectorAll('[data-utc-timestamp]');
    
    timestamps.forEach(element => {
      const utcString = element.getAttribute('data-utc-timestamp');
      const formatted = formatTimestamp(utcString);
      element.textContent = formatted;
    });
  }
  
  // Convert when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', convertTimestamps);
  } else {
    convertTimestamps();
  }
})();

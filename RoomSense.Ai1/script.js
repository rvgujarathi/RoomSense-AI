const LabMonitoringSystem = {
  currentSection: 'home',
  alerts: [],
  incidents: [],
  cameras: [],
  dropdownVisible: false,

  // Function to toggle dropdown visibility
  toggleDropdown: function() {
      this.dropdownVisible = !this.dropdownVisible;
      document.getElementById('dropdownMenu').style.display = this.dropdownVisible ? 'block' : 'none';
  },

  
  // Show feature content based on selection
  showFeature: function(feature) {
      const contentDiv = document.getElementById('content');
      this.dropdownVisible = false; // Close dropdown after selection
      document.getElementById('dropdownMenu').style.display = 'none'; // Hide dropdown menu

      switch(feature) {
          case 'real-time-data':
              contentDiv.innerHTML = this.getRealTimeDataContent();
              break;
          case 'alerts':
              contentDiv.innerHTML = this.getAlertsContent();
              break;
          case 'crowd-detection':
              contentDiv.innerHTML = this.getCrowdDetectionContent();
              break;
          case 'missing-items':
              contentDiv.innerHTML = this.getMissingItemsContent();
              break;
          case 'color-detection':
              contentDiv.innerHTML = this.getColorDetectionContent();
              break;
          case 'behavioral-anomaly':
              contentDiv.innerHTML = this.getBehavioralAnomalyContent();
              break;
          default:
              contentDiv.innerHTML = `<h1>Feature not found</h1>`;
      }
  },

  // Other existing methods...
};



// Event listeners for navigation
document.getElementById('homeBtn').addEventListener('click', () => LabMonitoringSystem.showSection('home'));
document.getElementById('realTimeBtn').addEventListener('click', () => LabMonitoringSystem.showSection('real-time-monitoring'));
document.getElementById('alertsBtn').addEventListener('click', () => LabMonitoringSystem.showSection('alerts'));
document.getElementById('reportsBtn').addEventListener('click', () => LabMonitoringSystem.showSection('reports'));
document.getElementById('settingsBtn').addEventListener('click', () => LabMonitoringSystem.showSection('settings'));

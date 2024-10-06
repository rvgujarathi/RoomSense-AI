document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".sidebar");
  const mainContent = document.querySelector(".main-content");
  const toggleBtn = document.querySelector(".toggle-btn");

  const loaderContainer = document.querySelector(".loader-container");
  const videoContainer = document.querySelector(".video-container");

  // Sidebar toggle functionality
  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("active");
    mainContent.classList.toggle("active");
    toggleBtn.classList.toggle("rotate"); // Rotate the button

    // Handle sidebar elements visibility
    const controls = document.querySelectorAll(
      ".controls, .stats, .fake-section h2"
    );
    controls.forEach((control) => {
      control.classList.toggle("active");
    });
  });

  // Simulate loading video
  setTimeout(() => {
    loaderContainer.style.display = "none";
    videoContainer.style.display = "flex"; // Show video container
  }, 2000); // Simulated loading time (2 seconds)
});

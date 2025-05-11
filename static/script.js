window.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  const html = document.documentElement;
  const savedTheme = localStorage.getItem("theme") || "light";

  html.setAttribute("data-theme", savedTheme);
  if (toggle) toggle.textContent = savedTheme === "dark" ? "☀️" : "🌙";

  if (toggle) {
      toggle.addEventListener("click", () => {
          const currentTheme = html.getAttribute("data-theme");
          const newTheme = currentTheme === "dark" ? "light" : "dark";
          html.setAttribute("data-theme", newTheme);
          toggle.textContent = newTheme === "dark" ? "☀️" : "🌙";
          localStorage.setItem("theme", newTheme);
      });
  }

  function typeText(element, text) {
      let index = 0;
      function typeChar() {
          if (index < text.length) {
              element.textContent += text.charAt(index);
              index++;
              setTimeout(typeChar, 30); 
          }
      }
      element.textContent = ""; 
      typeChar();
  }

  const beagleResponse = document.querySelector(".beagle-response");
  if (beagleResponse && beagleResponse.dataset.text) {
      typeText(beagleResponse, beagleResponse.dataset.text);
  }
});

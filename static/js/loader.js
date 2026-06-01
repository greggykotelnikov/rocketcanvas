document.addEventListener("DOMContentLoaded", () => {
  const loaderStr = `
    <div id="mk-loader">
      <div class="mk-gif-container">
        <img src="/static/images/loading_screen_animation_cars_moving.gif" class="mk-gif" alt="Loading...">
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML("beforeend", loaderStr);
  const loader = document.getElementById("mk-loader");
  const TRANSITION_MS = 900;

  // Clean up exit transition classes cleanly using transitionend to prevent snaps/glitches
  loader.addEventListener("transitionend", (e) => {
    if (e.propertyName === "transform" && loader.classList.contains("exit")) {
      loader.style.transition = "none";
      loader.classList.remove("exit");
      void loader.offsetWidth;
      loader.style.transition = "";
    }
  });

  document.querySelectorAll("a").forEach((link) => {
    if (
      link.hostname === window.location.hostname &&
      !link.target &&
      !link.href.includes("#")
    ) {
      link.addEventListener("click", (e) => {
        if (link.getAttribute("href")?.includes("logout")) return;

        e.preventDefault();
        const targetUrl = link.href;

        loader.classList.remove("exit");
        loader.classList.add("active");

        setTimeout(() => {
          window.location.href = targetUrl;
        }, TRANSITION_MS);
      });
    }
  });

  loader.classList.add("active");
  void loader.offsetWidth;
  loader.classList.remove("active");
  loader.classList.add("exit");
});

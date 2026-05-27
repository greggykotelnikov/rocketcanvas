document.addEventListener("DOMContentLoaded", () => {
  // Side-view sprites (user-provided)
  const octane = "/static/images/octane_sideview_for_loadingscreen.png";
  const dominus = "/static/images/dominus_sideview_for_loadingscreen.png";
  const fennec = "/static/images/fennec_sideview_for_loadingscreen.png";

  // 6-car parade, one direction (Mario Kart vibe)
  const cars = [octane, dominus, fennec, octane, dominus, fennec].map((src, i) => ({
    src,
    lane: (i % 3) + 1,
    delay: i * 0.08,
    speed: 1.05 + (i % 3) * 0.12, // small variation
  }));

  const carImgs = cars
    .map(
      (c) =>
        `<img src="${c.src}" class="mk-car lane-${c.lane}" alt="" style="animation-delay:${c.delay.toFixed(
          2
        )}s; animation-duration:${c.speed.toFixed(2)}s">`
    )
    .join("");

  const loaderStr = `
    <div id="mk-loader">
      <div class="mk-brand">RocketCanvas</div>
      <div class="mk-parade">${carImgs}</div>
    </div>
  `;
  document.body.insertAdjacentHTML("beforeend", loaderStr);
  const loader = document.getElementById("mk-loader");
  const TRANSITION_MS = 650;

  function replayParade() {
    loader.querySelectorAll(".mk-car").forEach((img) => {
      img.style.animation = "none";
      void img.offsetWidth;
      img.style.animation = "";
    });
  }

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
        replayParade();
        loader.classList.add("active");

        setTimeout(() => {
          window.location.href = targetUrl;
        }, TRANSITION_MS);
      });
    }
  });

  loader.classList.add("active");
  replayParade();
  void loader.offsetWidth;
  loader.classList.remove("active");
  loader.classList.add("exit");

  setTimeout(() => {
    loader.style.transition = "none";
    loader.classList.remove("exit");
    void loader.offsetWidth;
    loader.style.transition = "";
  }, TRANSITION_MS);
});

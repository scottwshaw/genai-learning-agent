document.addEventListener("DOMContentLoaded", function () {
  var dirname = document.querySelector("[data-dirname]").dataset.dirname;

  document.querySelectorAll("[data-item-key]").forEach(function (el) {
    var btn = document.createElement("button");
    btn.className = "interesting-toggle";
    btn.textContent = el.dataset.interesting === "true" ? "★" : "☆";
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var isInteresting = el.dataset.interesting !== "true";
      fetch("/brief/" + dirname + "/annotate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_key: el.dataset.itemKey, interesting: isInteresting }),
      }).then(function () {
        el.dataset.interesting = isInteresting ? "true" : "";
        btn.textContent = isInteresting ? "★" : "☆";
        el.classList.toggle("is-interesting", isInteresting);
      });
    });
    el.insertBefore(btn, el.firstChild);
  });
});

document.addEventListener("DOMContentLoaded", function () {
  var main = document.querySelector("[data-dirname]");
  var dirname = main.dataset.dirname;

  // Mark Reviewed toggle
  var reviewBtn = document.createElement("button");
  reviewBtn.className = "reviewed-toggle";
  var isReviewed = main.dataset.reviewed === "true";
  reviewBtn.textContent = isReviewed ? "✔ Reviewed" : "Mark Reviewed";
  if (isReviewed) reviewBtn.classList.add("is-reviewed");
  reviewBtn.addEventListener("click", function () {
    isReviewed = !isReviewed;
    fetch("/brief/" + dirname + "/annotate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_key: "_reviewed", interesting: isReviewed }),
    }).then(function () {
      reviewBtn.textContent = isReviewed ? "✔ Reviewed" : "Mark Reviewed";
      reviewBtn.classList.toggle("is-reviewed", isReviewed);
    });
  });
  main.insertBefore(reviewBtn, main.firstChild);

  // Star toggles for annotatable items
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

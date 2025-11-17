document.addEventListener("DOMContentLoaded", function () {
  const image = document.getElementById("pfpImage");
  const input = document.getElementById("pfpInput");

  image.addEventListener("click", () => input.click());
  document.querySelector(".edit-pfp").addEventListener("click", () => input.click());

  input.addEventListener("change", function () {
    if (this.files && this.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        image.src = e.target.result;
      }
      reader.readAsDataURL(this.files[0]);
    }
  });
});


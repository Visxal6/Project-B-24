const form = document.querySelector(".form-wizard");

if (form) {
  const steps = form.querySelectorAll(".step");
  const prevButton = form.querySelector(".prev-btn");
  const nextButton = form.querySelector(".next-btn");
  const submitButton = form.querySelector(".submit-btn");
  let currentStep = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.classList.toggle("current", i === index);
    });

    prevButton.hidden = index === 0;
    nextButton.hidden = index === steps.length - 1;
    submitButton.hidden = !nextButton.hidden;
  }

  function validateCurrentStep() {
    if (currentStep === 0) {
      const roleSelected = form.querySelector('input[name="role"]:checked');
      if (!roleSelected) {
        alert("Please choose if you are a Student or a CIO.");
        return false;
      }
    } else if (currentStep === 1) {
      const interestsSelected = form.querySelectorAll(
        'input[name="interests"]:checked'
      );
      if (!interestsSelected.length) {
        alert("Please pick at least one interest.");
        return false;
      }
    }
    return true;
  }

  nextButton.addEventListener("click", (e) => {
    e.preventDefault();
    if (!validateCurrentStep()) return;
    if (currentStep < steps.length - 1) {
      currentStep++;
      showStep(currentStep);
    }
  });

  prevButton.addEventListener("click", (e) => {
    e.preventDefault();
    if (currentStep > 0) {
      currentStep--;
      showStep(currentStep);
    }
  });

  form.addEventListener("submit", () => {
    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";
  });

  showStep(currentStep);
}

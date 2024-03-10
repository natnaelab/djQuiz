function updateFieldsVisibility(questionType) {
  document
    .querySelector(".choice-form-field")
    .classList.toggle("hidden", questionType !== "MULTIPLE_CHOICE");
  document
    .querySelector(".short-answer-field")
    .classList.toggle("hidden", questionType !== "SHORT_ANSWER");
}

function showDeleteChoiceDivs() {
  const deleteChoiceDivs = document.querySelectorAll(".delete-choice");
  deleteChoiceDivs.forEach((div) => {
    div.classList.remove("hidden");
  });
}

const choiceOptions = document.querySelectorAll(".choice-form");
const numChoices = choiceOptions.length;

if (numChoices > 2) showDeleteChoiceDivs();

function addChoiceOption() {
  const choiceOptions = document.querySelectorAll(".choice-form");
  const numChoices = choiceOptions.length;

  showDeleteChoiceDivs();

  if (numChoices >= 10) return;

  const choiceClone = choiceOptions[0].cloneNode(true);
  const formNamePrefix = `choice-${numChoices}-`;

  const inputEl = choiceClone.querySelector("input");
  const selectEl = choiceClone.querySelector("select");

  inputEl.name = formNamePrefix + "text";
  inputEl.id = `id_${inputEl.name}`;
  inputEl.value = "";

  selectEl.name = formNamePrefix + "is_correct";
  selectEl.id = `id_${selectEl.name}`;
  selectEl.value = "False";

  choiceOptions[0].parentElement.insertBefore(
    choiceClone,
    addOptionBtn.previousSibling
  );

  // increment choice formset total forms
  document
    .getElementById("id_choice-TOTAL_FORMS")
    .setAttribute("value", numChoices + 1);
}

const questionType = document.getElementById("id_question_type");
const addOptionBtn = document.getElementById("add-option");

if (questionType) {
  updateFieldsVisibility(questionType.value);

  questionType.addEventListener("change", (ev) => {
    updateFieldsVisibility(ev.target.value);
  });
}

if (addOptionBtn) addOptionBtn.addEventListener("click", addChoiceOption);

document.body.addEventListener("click", (ev) => {
  const choiceForms = document.querySelectorAll(".choice-form");
  const choiceFormCount = choiceForms.length;

  if (
    ev.target.tagName.toLowerCase() == "button" &&
    ev.target.id == "remove-option" &&
    choiceFormCount > 2
  ) {
    ev.target.closest(".choice-form").remove();
    const choiceTotalForms = document.getElementById("id_choice-TOTAL_FORMS");
    choiceTotalForms.value = parseInt(choiceTotalForms.value) - 1;

    if (choiceFormCount === 3) {
      choiceForms.forEach((form) =>
        form.querySelector(".delete-choice").classList.add("hidden")
      );
    }
  }

  // close modal
  const modal = document.querySelector('[id$="_modal"]');
  if (ev.target === modal) closeModal(modal.id);
});

const questionFormErrorCloseBtn = document.getElementById(
  "question-form-error-close"
);

if (questionFormErrorCloseBtn) {
  questionFormErrorCloseBtn.addEventListener("click", (_) => {
    questionFormErrorCloseBtn.parentElement.remove();
  });
}

const modalOverlay = document.getElementById("modal-backdrop");

function openModal(modalId) {
  modalOverlay.classList.remove("hidden");
  document.getElementById(modalId).classList.remove("hidden");
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add("hidden");
  modalOverlay.classList.add("hidden");
}

document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") {
    const modals = document.querySelectorAll('[id$="_modal"]');
    modals.forEach((modal) => closeModal(modal.id));
  }
});

function toggleCheckbox(element) {
  const checkbox = element.querySelector("input[type='checkbox']");
  checkbox.checked = !checkbox.checked;
}

function startCountdown() {
  const countdownInterval = setInterval(() => {
    const countdownInput = document.querySelector("input[name='countdown']");
    const countdownElement = document.getElementById("countdown");
    const countdown = parseInt(countdownInput.value) - 1;
    countdownInput.value = countdown;
    if (countdown >= 0) {
      const minutes = Math.floor(countdown / 60);
      const seconds = countdown % 60;
      countdownElement.innerText = `${minutes < 10 ? "0" : ""}${minutes}:${
        seconds < 10 ? "0" : ""
      }${seconds}`;
    } else {
      clearInterval(countdownInterval);
      const timeoutOverlay = document.getElementById("timeout-overlay");
      timeoutOverlay.classList.remove("hidden");
      setTimeout(() => {
        // reload page
        window.location.reload();
      }, 5000);
    }
  }, 1000);
}

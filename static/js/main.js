function updateFieldsVisibility(value) {
  document
    .querySelector(".choice-field")
    .classList.toggle("hidden", value !== "CHOICE");
  document
    .querySelector(".short-answer-field")
    .classList.toggle("hidden", value !== "SHORT_ANSWER");
}

function addChoiceOption() {
  const choiceOptions = document.querySelectorAll(".choice-form");
  const ChoiceOptionCount = choiceOptions.length;

  if (ChoiceOptionCount >= 10) return;

  const choiceClone = choiceOptions[0].cloneNode(true);

  const formNamePrefix = `form-${ChoiceOptionCount}-`;
  const inputEl = choiceClone.querySelector("input");
  const selectEl = choiceClone.querySelector("select");

  inputEl.name = formNamePrefix + "text";
  inputEl.id = `id_${inputEl.name}`;
  inputEl.value = "";

  selectEl.name = formNamePrefix + "is_correct";
  selectEl.id = `id_${selectEl.name}`;
  selectEl.value = "False";

  choiceOptions[0].parentNode.appendChild(choiceClone);
}

const questionType = document.getElementById("id_question_type");
const addOptionBtn = document.getElementById("add-option");
const removeOptionBtns = document.querySelectorAll("#remove-option");

updateFieldsVisibility(questionType.value);

questionType.addEventListener("change", (ev) => {
  updateFieldsVisibility(ev.target.value);
});

addOptionBtn.addEventListener("click", addChoiceOption);

document.body.addEventListener("click", (ev) => {
  if (
    ev.target.tagName.toLowerCase() == "button" &&
    ev.target.id == "remove-option" &&
    document.querySelectorAll(".choice-form").length > 2
  ) {
    ev.target.closest(".choice-form").remove();
  }
});

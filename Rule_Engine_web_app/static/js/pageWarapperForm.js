// Get the select element
const selectElement = document.getElementById("repayment_term_month");

// Loop from 84 down to 0
for (let i = 84; i >= 1; i--) {
  // Create a new option element
  const option = document.createElement("option");
  // Set the value and text for the option
  option.value = i;
  option.text = i;
  // Append the option to the select element
  selectElement.appendChild(option);
}
const selectElementyear = document.getElementById("asset_manufacture_year");

// Loop from 2024 down to 2000
for (let i = 2024; i >= 2000; i--) {
  // Create a new option element
  const option1 = document.createElement("option");
  // Set the value and text for the option
  option1.value = i;
  option1.text = i;
  // Append the option to the select element
  selectElementyear.appendChild(option1);
}

let eDate = null;

setTimeout(function() {
  try {
    document.getElementById('messages').style.display='none';
  } catch {
    console.log("no messages");
  }
}, 5000); //

function openmodal() {
  e = document.getElementById('mdl-add');
  e.classList.add('is-active');
}

function closemodal() {
  e = document.getElementById('mdl-add');
  e.classList.remove('is-active');
}

function addEntry(ledgerID) {

  eDescription = document.getElementById('description').value;
  eAmount = document.getElementById('amount').value;
  catField = document.getElementById('category');
  eCategory = catField.options[catField.selectedIndex].id;
  typeField = document.getElementById('ttype');
  eType = typeField.options[typeField.selectedIndex].id;
  console.log("you clicked add");
  console.log(ledgerID)
  console.log("values are: " + eDescription + " " + eAmount + " " + eCategory + " " + eType + " " + eDate);
  document.getElementById('description').value = '';
  document.getElementById('amount').value = '';

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "./api/addEntry", true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
    desc: eDescription,
    amount: eAmount,
    category: eCategory,
    type: eType,
    date: eDate,
    ledger: ledgerID
  }));

  closemodal();
}

var example = flatpickr('#entrydate', {
  onChange: () => eDate = this.example.selectedDates,
  altInput: true,
  altFormat: "F j, Y",
  dateFormat: "F j, Y"
});

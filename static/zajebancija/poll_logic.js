let clickCount = 0;

document.addEventListener("DOMContentLoaded", function () {
  const btnDa = document.querySelector(".tricolor-button-smarje");
  const leftarea = document.getElementById("leftarea");
  const rightarea = document.getElementById("rightarea");
  const centerarea = document.getElementById("centerarea");

  if (!btnDa || !leftarea || !rightarea || !centerarea) {
    console.error("One or more elements not found:", {
      btnDa,
      leftarea,
      rightarea,
      centerarea,
    });
    return;
  }

  if (btnDa) {
    btnDa.addEventListener("click", function (e) {
      clickCount++;
      if (clickCount < 4) {
        e.preventDefault();
        if(clickCount === 1) {
          leftarea.appendChild(btnDa);
    } else if(clickCount === 2) {
          rightarea.appendChild(btnDa);
    } else if(clickCount === 3) {
          centerarea.appendChild(btnDa)
  }
        else if(clickCount === 4){
          alert('Glas šteje ali pojdi na rezultate!');
        }

      }
    });
  }
});

  const form = document.getElementById("filter_form");

  form.addEventListener("change", async function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const query = new URLSearchParams(formData).toString();

    const response = await fetch(`/?${query}`, {
      headers: { "X-Requested-With": "XMLHttpRequest" }
    });

    const html = await response.text();
    document.getElementById("table_body").innerHTML = html;
  });


  
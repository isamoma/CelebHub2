document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("themeToggle");
  const html = document.documentElement;

  // Load saved theme preference
  if (localStorage.theme === "dark" || 
      (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
    html.classList.add("dark");
  } else {
    html.classList.remove("dark");
  }

  toggle.addEventListener("click", () => {
    html.classList.toggle("dark");
    localStorage.theme = html.classList.contains("dark") ? "dark" : "light";
  });
});

document.getElementById('payNow').addEventListener('click', async () => {
    const phone = prompt("Enter your M-Pesa phone number (254...)");
    const amount = prompt("Enter amount to pay:");
    
    if (phone && amount) {
        const res = await fetch('/pay', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone, amount})
        });
        const data = await res.json();
        alert("Payment initiated! Check your phone to enter PIN.");
    }
});

document.getElementById("mpesaForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());
  const msg = document.getElementById("mpesaMessage");

  msg.innerText = "Processing payment... please check your phone 📱";

  const res = await fetch("/pay", {
    method: "POST",
    body: formData,
  });
  const result = await res.json();

  if (result.ResponseCode === "0") {
    msg.innerText = "Payment prompt sent! Enter your M-Pesa PIN.";
  } else {
    msg.innerText = "Payment failed: " + (result.errorMessage || "Please try again.");
  }
});
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

fetch(`/delete_celebrity/${id}`, {
  method: "POST",
  headers: {
    "X-CSRFToken": csrfToken
  }
});


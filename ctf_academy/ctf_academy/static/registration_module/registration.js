const form = document.getElementById("registrationForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const message = document.getElementById("message");

// Use localStorage to simulate a database
const getUsers = () => JSON.parse(localStorage.getItem("users") || "[]");
const saveUsers = (users) => localStorage.setItem("users", JSON.stringify(users));

// Assign role based on domain rule
function assignRole(email) {
  if (email.endsWith("@academy.edu")) {
    return "Admin";
  }
  return "User";
}

form.addEventListener("submit", function (e) {
  e.preventDefault();
  message.textContent = "";
  message.className = "";

  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();
  const users = getUsers();

  // Regex for email and password policy
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const passwordPolicy = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

  // 4. Missing Required Fields
  if (!email || !password) {
    message.textContent = "Email and password are required.";
    message.className = "error";
    return;
  }

  // 5. Invalid Email Format
  if (!emailRegex.test(email)) {
    message.textContent = "Please enter a valid email address.";
    message.className = "error";
    return;
  }

  // Weak password
  if (!passwordPolicy.test(password)) {
    message.textContent =
      "Password must be at least 8 characters, include uppercase, lowercase, and a number.";
    message.className = "error";
    return;
  }

  // 6. Email Already Registered
  if (users.find((u) => u.email === email)) {
    message.textContent = "This email is already registered.";
    message.className = "error";
    return;
  }

  // 1. Role Assignment
  const role = assignRole(email);

  // 2. Welcome Email (simulated in console)
  console.log(`📧 Welcome email sent to ${email}.`);
  console.log(`Please confirm your email by clicking the link: 
  http://localhost:5500/ctf_academy/templates/register_module/register_confirmation.html?email=${encodeURIComponent(email)}`);

  // 3. Email Confirmation (simulate by storing verified=false)
  users.push({ email, password, role, verified: false });
  saveUsers(users);

  message.textContent = "Registration successful! Please check your email to confirm.";
  message.className = "success";

  // Clear inputs
  emailInput.value = "";
  passwordInput.value = "";

  // Redirect to confirmation page simulation after 2 seconds
  setTimeout(() => {
    window.location.href = `/ctf_academy/templates/register_module/register_confirmation.html?email=${encodeURIComponent(email)}`;
  }, 2000);
});

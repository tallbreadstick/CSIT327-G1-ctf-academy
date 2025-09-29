// num1: Login with Token - validate credentials and return a JWT token
// num2: Role Based Access Control - assign permissions based on role at login
// num3: Successful Authentication - access protected route with valid token
// num4: Invalid Token - return error if token is invalid or expired
// num5: Missing Token - return error if token is not provided
// num6: Incorrect Credentials - return error if email/password is wrong

document.getElementById("loginForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const message = document.getElementById("message");

  // Simulate fetching users from "database" (localStorage)
  const users = JSON.parse(localStorage.getItem("users") || "[]");

  // Find user
  const user = users.find(u => u.email === email);

  // num6: Incorrect Credentials
  if (!user || user.password !== password) {
    message.textContent = "Invalid login credentials.";
    message.style.color = "red";
    return;
  }

  // num1: Login with Token
  // TODO: Generate JWT token here for real implementation
  const token = "fake-jwt-token"; // placeholder

  // num2: Role Based Access Control
  if (user.role === "Admin") {
    message.style.color = "green";
    message.textContent = "Welcome Admin! Redirecting to Admin Dashboard...";
    setTimeout(() => {
      window.location.href = "/ctf_academy/templates/dashboard_module/admin_dashboard.html"; // Admin dashboard
    }, 1500);
  } else if (user.role === "User") {
    message.style.color = "green";
    message.textContent = "Welcome User! Redirecting to User Dashboard...";
    setTimeout(() => {
      window.location.href = "/ctf_academy/templates/dashboard_module/user_dashboard.html"; // User dashboard
    }, 1500);
  } else {
    // num3: Successful Authentication fallback
    message.style.color = "red";
    message.textContent = "Invalid user role.";
  }

  // num4 & num5: Invalid or Missing Token
  // TODO: Handle token validation on protected routes
});

function handleLogin(event) {
    if (event) {
        event.preventDefault();
    }

    const loginForm = document.getElementById('loginForm');

    if (loginForm && !loginForm.reportValidity()) {
        return;
    }
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;
    const nextUrlInput = document.getElementById('nextUrlInput') ? document.getElementById('nextUrlInput').value : '/';

    loginUser(usernameInput, passwordInput, nextUrlInput);
}

function handleRegister(event) {
    if (event) {
        event.preventDefault();
    }

    const registerForm = document.getElementById('registerForm');

    if (registerForm && !registerForm.reportValidity()) {
        return;
    }
    const usernameInput = document.getElementById('username1').value.trim();
    const emailInput = document.getElementById('email').value.trim();
    const passwordInput = document.getElementById('password1').value;
    const confirmPasswordInput = document.getElementById('confirm_password').value;

    registerUser(usernameInput,emailInput,passwordInput,confirmPasswordInput);
}
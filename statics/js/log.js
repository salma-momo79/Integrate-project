const loginEye = document.getElementById('login-eye');
    const loginPass = document.getElementById('login-pass');

    loginEye.addEventListener('click', () => {
      const type = loginPass.getAttribute('type') === 'password' ? 'text' : 'password';
      loginPass.setAttribute('type', type);
      loginEye.classList.toggle('ri-eye-line');
      loginEye.classList.toggle('ri-eye-off-line');
    });
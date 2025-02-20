document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const lightIcon = document.querySelector('.light-mode-icon');
    const darkIcon = document.querySelector('.dark-mode-icon');

    function setTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
            lightIcon.style.display = 'none';
            darkIcon.style.display = 'inline';
        } else {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            lightIcon.style.display = 'inline';
            darkIcon.style.display = 'none';
        }
    }

    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Theme toggle handler
    themeToggle.addEventListener('click', () => {
        const newTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);
        setTheme(newTheme);
    });
});
// Simple interactions for demonstration
document.addEventListener('DOMContentLoaded', function () {
    // Toggle mobile menu
    const menuToggle = document.querySelector('.menu-toggle');
    const navbarNav = document.querySelector('.navbar-nav');
    const searchForm = document.querySelector('.search-form');

    if (menuToggle) {
        menuToggle.addEventListener('click', function () {
            navbarNav.classList.toggle('mobile-active');
            searchForm.classList.toggle('mobile-active');
            menuToggle.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.navbar-container')) {
            navbarNav.classList.remove('mobile-active');
            searchForm.classList.remove('mobile-active');
            menuToggle.classList.remove('active');
        }
    });

    // If this is the add-todo form on the index page, don't override its submit behavior.
    // Let Flask handle POST / so the todo is created server-side.
    const addForm = document.querySelector('form[action="/"]');
    if (addForm) {
        // Intentionally do not call preventDefault().
        // You can add non-blocking UI feedback here if desired.
        addForm.addEventListener('submit', function () {
            // allow normal submission
        });
    }

    // Important: do NOT intercept clicks on update/delete links that point to
    // server routes like /update/<sno> or /delete/<sno>. Those should navigate
    // normally so Flask can render the update page or perform the delete.
});

// Floating + button: navigate to the dedicated add page
document.addEventListener('DOMContentLoaded', function () {
    const floatingBtn = document.querySelector('.floating-btn');
    if (!floatingBtn) return;

    floatingBtn.addEventListener('click', function (e) {
        e.preventDefault();
        // go to add page
        window.location.href = '/add';
    });
});
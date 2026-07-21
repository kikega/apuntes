(function() {
    'use strict';

    // Dark mode init (must run before DOMContentLoaded to avoid flash)
    if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Sidebar dropdowns
        window.toggleSidebarDropdown = function(id) {
            const dropdown = document.getElementById('dropdown-' + id);
            const chevron = document.getElementById('chevron-' + id);
            if (dropdown && chevron) {
                dropdown.classList.toggle('hidden');
                chevron.classList.toggle('rotate-180');
            }
        };

        // Auto-expand active category/family
        const activeFamilyLinks = document.querySelectorAll('[id^="dropdown-cat-"] a.bg-slate-100\\/50, [id^="dropdown-cat-"] a.text-primary-600, [id^="dropdown-cat-"] a.dark\\:text-amber-500');
        activeFamilyLinks.forEach(function(link) {
            const parentDropdown = link.closest('[id^="dropdown-cat-"]');
            if (parentDropdown) {
                parentDropdown.classList.remove('hidden');
                const catId = parentDropdown.id.replace('dropdown-', '');
                const chevron = document.getElementById('chevron-' + catId);
                if (chevron) chevron.classList.add('rotate-180');
            }
        });

        const activeCatWrapper = document.querySelector('.bg-primary-50\\/50, .dark\\:bg-darkBg');
        if (activeCatWrapper) {
            const parentDiv = activeCatWrapper.closest('.space-y-1');
            if (parentDiv) {
                const dropdown = parentDiv.querySelector('[id^="dropdown-cat-"]');
                if (dropdown) {
                    dropdown.classList.remove('hidden');
                    const catId = dropdown.id.replace('dropdown-', '');
                    const chevron = document.getElementById('chevron-' + catId);
                    if (chevron) chevron.classList.add('rotate-180');
                }
            }
        }

        // Mobile sidebar
        const openBtn = document.getElementById('open-sidebar-btn');
        const closeBtn = document.getElementById('close-sidebar-btn');
        const sidebar = document.getElementById('sidebar');
        if (openBtn && sidebar) {
            openBtn.addEventListener('click', function() { sidebar.classList.remove('-translate-x-full'); });
        }
        if (closeBtn && sidebar) {
            closeBtn.addEventListener('click', function() { sidebar.classList.add('-translate-x-full'); });
        }

        // Dark mode toggle
        const themeToggleBtn = document.getElementById('theme-toggle');
        const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
        const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

        if (document.documentElement.classList.contains('dark')) {
            themeToggleLightIcon.classList.remove('hidden');
        } else {
            themeToggleDarkIcon.classList.remove('hidden');
        }

        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', function() {
                themeToggleDarkIcon.classList.toggle('hidden');
                themeToggleLightIcon.classList.toggle('hidden');
                if (document.documentElement.classList.contains('dark')) {
                    document.documentElement.classList.remove('dark');
                    localStorage.setItem('color-theme', 'light');
                } else {
                    document.documentElement.classList.add('dark');
                    localStorage.setItem('color-theme', 'dark');
                }
            });
        }
    });
})();

(function() {
    'use strict';

    const STATE = {
        favUrlTmpl: null,  // '/ajax/apunte/{id}/favorito/'
        csrfToken: null,
    };

    window.initDetail = function(config) {
        STATE.favUrlTmpl = config.favUrlTmpl;
        STATE.csrfToken = config.csrfToken;
    };

    window.toggleFavorito = function(apunteId) {
        const btn = document.getElementById('fav-btn-' + apunteId);
        const label = document.getElementById('fav-label-' + apunteId);
        const url = STATE.favUrlTmpl.replace('{id}', apunteId);
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': STATE.csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.favorito) {
                label.textContent = 'Favorito';
                btn.classList.remove('bg-slate-50', 'dark:bg-darkBg', 'text-slate-500', 'dark:text-slate-400', 'border-slate-200', 'dark:border-darkBorder', 'hover:text-amber-500');
                btn.classList.add('bg-amber-50', 'dark:bg-amber-950/30', 'text-amber-600', 'dark:text-amber-400', 'border-amber-200', 'dark:border-amber-800');
                btn.querySelector('svg').setAttribute('fill', 'currentColor');
            } else {
                label.textContent = 'Guardar';
                btn.classList.remove('bg-amber-50', 'dark:bg-amber-950/30', 'text-amber-600', 'dark:text-amber-400', 'border-amber-200', 'dark:border-amber-800');
                btn.classList.add('bg-slate-50', 'dark:bg-darkBg', 'text-slate-500', 'dark:text-slate-400', 'border-slate-200', 'dark:border-darkBorder', 'hover:text-amber-500');
                btn.querySelector('svg').setAttribute('fill', 'none');
            }
        });
    };

    window.copyToClipboard = function() {
        navigator.clipboard.writeText(window.location.href).then(function() {
            var label = document.getElementById('copy-label');
            label.textContent = '¡Copiado!';
            setTimeout(function() { label.textContent = 'Copiar enlace'; }, 2000);
        });
    };

    // Close export dropdown on click outside
    document.addEventListener('click', function(e) {
        var dd = document.getElementById('export-dropdown');
        if (dd && !dd.classList.contains('hidden') && !e.target.closest('#export-dropdown') && !e.target.closest('button[onclick*="export-dropdown"]')) {
            dd.classList.add('hidden');
        }
    });
})();

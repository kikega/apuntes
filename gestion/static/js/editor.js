(function() {
    'use strict';

    var autoSaveTimer = null;
    var STORAGE_KEY = null;
    var STATE = {
        previewUrl: null,
        tagCreateUrl: null,
        imageUploadUrl: null,
        csrfToken: null,
    };

    window.initEditor = function(config) {
        STATE.previewUrl = config.previewUrl;
        STATE.tagCreateUrl = config.tagCreateUrl;
        STATE.imageUploadUrl = config.imageUploadUrl;
        STATE.csrfToken = config.csrfToken;
        STORAGE_KEY = config.storageKey || 'apunte_draft';
        restoreDraft();
        bindAutoSave();
    };

    window.toggleHelpPanel = function() {
        var el = document.getElementById('help-panel');
        if (el) el.classList.toggle('hidden');
    };

    window.insertMarkup = function(type) {
        var textarea = document.getElementById('id_contenido');
        var formato = document.getElementById('id_formato').value;
        if (!textarea) return;
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var text = textarea.value;
        var selected = text.substring(start, end);
        var before = '', after = '', placeholder = '';

        if (formato === 'MD') {
            var map = {
                bold: ['**', '**', 'texto en negrita'],
                italic: ['*', '*', 'texto en cursiva'],
                h1: ['# ', '\n', 'Título 1'],
                h2: ['## ', '\n', 'Título 2'],
                code_inline: ['`', '`', 'código'],
                code_block: ['```python\n', '\n```', '# código'],
                link: ['[', '](url)', 'texto del enlace'],
                ul: ['- ', '', 'Elemento'],
                ol: ['1. ', '', 'Elemento'],
                table: ['\n| Cabecera 1 | Cabecera 2 |\n| --- | --- |\n| Celda 1 | Celda 2 |\n', '', ''],
            };
            if (map[type]) { before = map[type][0]; after = map[type][1]; placeholder = map[type][2]; }
        } else {
            var len = Math.max((selected || 'Título').length, 4);
            var mapRst = {
                bold: ['**', '**', 'texto en negrita'],
                italic: ['*', '*', 'texto en cursiva'],
                h1: ['', '\n' + '='.repeat(len) + '\n', 'Título 1'],
                h2: ['', '\n' + '-'.repeat(len) + '\n', 'Título 2'],
                code_inline: ['``', '``', 'código'],
                code_block: ['.. code-block:: python\n\n    ', '', '# código'],
                link: ['`', ' <url>`_', 'texto del enlace'],
                ul: ['* ', '', 'Elemento'],
                ol: ['#. ', '', 'Elemento'],
                table: ['\n+------------+------------+\n| Cabecera 1 | Cabecera 2 |\n+============+============+\n| Celda 1    | Celda 2    |\n+------------+------------+\n', '', ''],
            };
            if (mapRst[type]) { before = mapRst[type][0]; after = mapRst[type][1]; placeholder = mapRst[type][2]; }
        }

        var insert = selected || placeholder;
        var replacement = before + insert + after;
        if (formato === 'RST' && (type === 'h1' || type === 'h2') && !selected) {
            var ch = type === 'h1' ? '=' : '-';
            replacement = insert + '\n' + ch.repeat(insert.length) + '\n';
        }
        textarea.value = text.substring(0, start) + replacement + text.substring(end);
        textarea.focus();
        textarea.setSelectionRange(start + before.length, start + before.length + insert.length);
        triggerAutoSave();
    };

    window.switchEditorTab = function(tab) {
        var be = document.getElementById('tab-btn-editor');
        var bp = document.getElementById('tab-btn-preview');
        var ce = document.getElementById('editor-container');
        var cp = document.getElementById('preview-container');
        if (!be || !bp || !ce || !cp) return;
        var active = ['border-primary-600', 'text-primary-600', 'dark:text-amber-500', 'dark:border-amber-500'];
        var inactive = ['border-transparent', 'text-slate-500', 'dark:text-slate-400'];
        if (tab === 'editor') {
            be.classList.add.apply(be.classList, active); be.classList.remove.apply(be.classList, inactive);
            bp.classList.add.apply(bp.classList, inactive); bp.classList.remove.apply(bp.classList, active);
            ce.classList.remove('hidden'); cp.classList.add('hidden');
        } else {
            bp.classList.add.apply(bp.classList, active); bp.classList.remove.apply(bp.classList, inactive);
            be.classList.add.apply(be.classList, inactive); be.classList.remove.apply(be.classList, active);
            ce.classList.add('hidden'); cp.classList.remove('hidden');
            loadPreview();
        }
    };

    function loadPreview() {
        var cp = document.getElementById('preview-container');
        if (!cp) return;
        cp.innerHTML = '<div class="flex items-center justify-center py-16"><svg class="animate-spin h-8 w-8 text-primary-600 dark:text-amber-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg></div>';
        var fd = new FormData();
        fd.append('contenido', document.getElementById('id_contenido').value);
        fd.append('formato', document.getElementById('id_formato').value);
        var ai = document.getElementById('apunte-id-data');
        if (ai) fd.append('apunte_id', ai.value);
        fetch(STATE.previewUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': STATE.csrfToken },
            body: fd
        })
        .then(function(r) { return r.text(); })
        .then(function(html) { cp.innerHTML = html; })
        .catch(function(e) { cp.innerHTML = '<div class="text-rose-500 p-4">Error: ' + e.message + '</div>'; });
    }

    function triggerAutoSave() {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(function() {
            var data = {
                contenido: document.getElementById('id_contenido').value,
                titulo: document.getElementById('id_titulo') ? document.getElementById('id_titulo').value : '',
            };
            try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch(e) {}
        }, 2000);
    }

    function restoreDraft() {
        var saved;
        try { saved = localStorage.getItem(STORAGE_KEY); } catch(e) { return; }
        if (!saved) return;
        try {
            var data = JSON.parse(saved);
            var ta = document.getElementById('id_contenido');
            if (data.contenido && ta && ta.value === '') {
                ta.value = data.contenido;
            }
        } catch(e) {}
    }

    function bindAutoSave() {
        var ta = document.getElementById('id_contenido');
        if (ta) ta.addEventListener('input', triggerAutoSave);
    }

    // Image upload
    document.addEventListener('DOMContentLoaded', function() {
        var uploadBtn = document.getElementById('upload-image-btn');
        var fileInput = document.getElementById('image-upload-input');
        if (uploadBtn && fileInput) {
            uploadBtn.addEventListener('click', function() { fileInput.click(); });
        }
    });

    window.uploadImage = function(input) {
        if (!input || !input.files.length) return;
        var file = input.files[0];
        var fd = new FormData();
        fd.append('imagen', file);
        fd.append('csrfmiddlewaretoken', STATE.csrfToken);
        var ai = document.getElementById('apunte-id-data');
        if (ai) fd.append('apunte_id', ai.value);
        fetch(STATE.imageUploadUrl, { method: 'POST', body: fd })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.url) {
                var ta = document.getElementById('id_contenido');
                var fmt = document.getElementById('id_formato').value;
                var md = fmt === 'MD' ? '![' + (data.descripcion || 'imagen') + '](' + data.url + ')' : '.. image:: ' + data.url + '\n   :alt: ' + (data.descripcion || 'imagen');
                ta.value += '\n' + md + '\n';
                triggerAutoSave();
            }
        })
        .catch(function() { alert('Error al subir imagen'); });
        input.value = '';
    };

    window.handleDrop = function(event) {
        event.preventDefault();
        var file = event.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            var input = document.getElementById('dropzone-input');
            if (input) {
                var dt = new DataTransfer();
                dt.items.add(file);
                input.files = dt.files;
                window.uploadImage(input);
            }
        }
    };

    window.handleDropFile = function(input) { window.uploadImage(input); };

    document.addEventListener('DOMContentLoaded', function() {
        var dz = document.getElementById('drop-zone');
        if (dz) {
            dz.addEventListener('click', function() {
                var inp = document.getElementById('dropzone-input');
                if (inp) inp.click();
            });
        }
    });

    window.createTagAndSelect = function() {
        var input = document.getElementById('new-tag-input');
        var name = (input && input.value.trim()) || '';
        if (!name) return;
        input.disabled = true;
        fetch(STATE.tagCreateUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': STATE.csrfToken },
            body: JSON.stringify({ nombre: name }),
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                var sel = document.getElementById('id_tags');
                if (sel) {
                    var opt = document.createElement('option');
                    opt.value = data.item.id; opt.text = data.item.nombre; opt.selected = true;
                    sel.appendChild(opt);
                }
                input.value = '';
            } else {
                alert((data.errors && data.errors.nombre) || 'Error al crear etiqueta');
            }
        })
        .catch(function() { alert('Error de conexión'); })
        .finally(function() { input.disabled = false; if (input) input.focus(); });
    };
})();

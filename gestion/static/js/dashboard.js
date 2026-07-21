(function() {
    'use strict';

    var STATE = {
        modalType: null,
        modalMode: null,
        editId: null,
        deleteType: null,
        deleteId: null,
    };

    var URLS = {};

    window.initDashboard = function(config) {
        URLS = config.urls;
    };

    function getCsrfToken() {
        var c = document.cookie.split(';').find(function(c) { return c.trim().startsWith('csrftoken='); });
        return c ? c.trim().split('=')[1] : '';
    }

    async function ajaxPost(url, data) {
        var resp = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify(data),
        });
        return { ok: resp.ok, status: resp.status, data: await resp.json() };
    }

    function toSlug(str) {
        return str.toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9\s-]/g, '')
            .trim().replace(/[\s_]+/g, '-')
            .replace(/-+/g, '-');
    }

    document.addEventListener('DOMContentLoaded', function() {
        var nombreField = document.getElementById('field-nombre');
        var slugField = document.getElementById('field-slug');
        if (nombreField && slugField) {
            nombreField.addEventListener('input', function() {
                if (!slugField.dataset.manualEdit) {
                    slugField.value = toSlug(this.value);
                }
            });
            slugField.addEventListener('input', function() {
                this.dataset.manualEdit = this.value ? 'true' : '';
            });
        }

        var openPanel = document.getElementById('btn-open-taxonomy-panel');
        var closePanel = document.getElementById('btn-close-taxonomy-panel');
        var panel = document.getElementById('taxonomy-panel');
        if (openPanel && panel) {
            openPanel.addEventListener('click', function() {
                panel.classList.remove('hidden');
                panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }
        if (closePanel && panel) {
            closePanel.addEventListener('click', function() { panel.classList.add('hidden'); });
        }

        var tabs = document.getElementById('taxonomy-tabs');
        if (tabs) {
            tabs.addEventListener('click', function(e) {
                var btn = e.target.closest('.taxonomy-tab-btn');
                if (!btn) return;
                var tab = btn.dataset.tab;
                document.querySelectorAll('.taxonomy-tab-btn').forEach(function(b) {
                    b.classList.remove('active-tab', 'border-primary-600', 'text-primary-600', 'dark:text-primary-400', 'dark:border-primary-400');
                    b.classList.add('border-transparent', 'text-slate-500');
                });
                btn.classList.add('active-tab', 'border-primary-600', 'text-primary-600', 'dark:text-primary-400', 'dark:border-primary-400');
                btn.classList.remove('border-transparent', 'text-slate-500');
                document.querySelectorAll('.taxonomy-tab-content').forEach(function(c) { c.classList.add('hidden'); });
                document.getElementById('tab-' + tab).classList.remove('hidden');
            });
        }

        var catSelect = document.getElementById('field-categoria');
        if (catSelect) {
            catSelect.addEventListener('change', async function() {
                var catId = this.value;
                var famSelect = document.getElementById('field-familia');
                famSelect.innerHTML = '<option value="">Cargando...</option>';
                famSelect.disabled = true;
                if (!catId) {
                    famSelect.innerHTML = '<option value="">— Primero selecciona una categoría —</option>';
                    famSelect.disabled = false;
                    return;
                }
                try {
                    var resp = await fetch(URLS.familiasPorCategoria + '?categoria_id=' + catId);
                    var json = await resp.json();
                    famSelect.innerHTML = json.familias.length
                        ? '<option value="">— Selecciona una familia —</option>' + json.familias.map(function(f) { return '<option value="' + f.id + '">' + f.nombre + '</option>'; }).join('')
                        : '<option value="">No hay familias en esta categoría</option>';
                } catch(e) {
                    famSelect.innerHTML = '<option value="">Error al cargar familias</option>';
                }
                famSelect.disabled = false;
            });
        }

        // Theme search filter
        var searchInput = document.getElementById('theme-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                var val = e.target.value.toLowerCase().trim();
                document.querySelectorAll('.theme-card').forEach(function(card) {
                    var name = card.getAttribute('data-theme-name') || '';
                    card.classList.toggle('hidden', val.length > 0 && !name.includes(val));
                });
            });
        }
    });

    window.openCreateModal = function(type) {
        STATE.modalType = type;
        STATE.modalMode = 'create';
        STATE.editId = null;
        resetModalForm();
        setModalTitle(type, 'create');
        showHideFields(type);
        openModal('crud-modal');
    };

    window.openEditModal = function(type, id, nombre, slug, descripcion, extra1Id, extra1Nombre, extra2Id, extra2Nombre) {
        STATE.modalType = type;
        STATE.modalMode = 'edit';
        STATE.editId = id;
        resetModalForm();
        setModalTitle(type, 'edit');
        showHideFields(type);
        document.getElementById('field-nombre').value = nombre;
        document.getElementById('field-slug').value = slug;
        document.getElementById('field-descripcion').value = descripcion || '';
        if (type === 'familia' && extra1Id) {
            document.getElementById('field-categoria').value = extra1Id;
        }
        if (type === 'tema' && extra2Id) {
            document.getElementById('field-categoria').value = extra2Id;
            loadFamiliasPorCategoria(extra2Id, extra1Id);
        }
        openModal('crud-modal');
    };

    async function loadFamiliasPorCategoria(catId, selectFamiliaId) {
        var famSelect = document.getElementById('field-familia');
        famSelect.innerHTML = '<option value="">Cargando...</option>';
        famSelect.disabled = true;
        try {
            var resp = await fetch(URLS.familiasPorCategoria + '?categoria_id=' + catId);
            var json = await resp.json();
            famSelect.innerHTML = json.familias.length
                ? '<option value="">— Selecciona una familia —</option>' + json.familias.map(function(f) { return '<option value="' + f.id + '" ' + (f.id == selectFamiliaId ? 'selected' : '') + '>' + f.nombre + '</option>'; }).join('')
                : '<option value="">No hay familias en esta categoría</option>';
        } catch(e) {
            famSelect.innerHTML = '<option value="">Error al cargar familias</option>';
        }
        famSelect.disabled = false;
    }

    function setModalTitle(type, mode) {
        var labels = { categoria: 'Categoría', familia: 'Familia', tema: 'Tema' };
        var actions = { create: 'Nueva', edit: 'Editar' };
        document.getElementById('crud-modal-title').textContent = actions[mode] + ' ' + labels[type];
    }

    function showHideFields(type) {
        var catWrapper = document.getElementById('field-categoria-wrapper');
        var famWrapper = document.getElementById('field-familia-wrapper');
        catWrapper.classList.toggle('hidden', type === 'categoria');
        famWrapper.classList.toggle('hidden', type !== 'tema');
        if (type !== 'tema') {
            document.getElementById('field-familia').innerHTML = '<option value="">— Primero selecciona una categoría —</option>';
        }
    }

    function resetModalForm() {
        document.getElementById('field-nombre').value = '';
        document.getElementById('field-slug').value = '';
        document.getElementById('field-slug').dataset.manualEdit = '';
        document.getElementById('field-descripcion').value = '';
        document.getElementById('field-categoria').value = '';
        document.getElementById('crud-error-global').classList.add('hidden');
        clearFieldErrors();
        setSubmitLoading(false);
    }

    function clearFieldErrors() {
        ['nombre', 'categoria_id', 'familia_id'].forEach(function(field) {
            var el = document.getElementById('error-' + field);
            if (el) {
                el.classList.add('hidden');
                var span = el.querySelector('span');
                if (span) span.textContent = '';
            }
        });
    }

    function showFieldError(field, message) {
        var el = document.getElementById('error-' + field);
        if (el) {
            el.classList.remove('hidden');
            var span = el.querySelector('span');
            if (span) span.textContent = message;
        }
    }

    function setSubmitLoading(loading) {
        var btn = document.getElementById('crud-submit-btn');
        var icon = document.getElementById('crud-submit-icon');
        var spinner = document.getElementById('crud-submit-spinner');
        var label = document.getElementById('crud-submit-label');
        btn.disabled = loading;
        if (icon) icon.classList.toggle('hidden', loading);
        if (spinner) spinner.classList.toggle('hidden', !loading);
        if (label) label.textContent = loading ? 'Guardando...' : 'Guardar';
    }

    window.handleModalSubmit = async function(event) {
        event.preventDefault();
        clearFieldErrors();
        var globalEl = document.getElementById('crud-error-global');
        if (globalEl) globalEl.classList.add('hidden');
        setSubmitLoading(true);

        var nombre = document.getElementById('field-nombre').value.trim();
        var descripcion = document.getElementById('field-descripcion').value.trim();
        var slug = document.getElementById('field-slug').value.trim();
        var categoriaId = document.getElementById('field-categoria').value;
        var familiaId = document.getElementById('field-familia').value;

        var payload = { nombre: nombre, descripcion: descripcion, slug: slug };
        if (STATE.modalType === 'familia') payload.categoria_id = categoriaId;
        if (STATE.modalType === 'tema') payload.familia_id = familiaId;

        var urlMap = {
            categoria: { create: URLS.categoriaCreate, edit: URLS.categoriaUpdate },
            familia: { create: URLS.familiaCreate, edit: URLS.familiaUpdate },
            tema: { create: URLS.temaCreate, edit: URLS.temaUpdate },
        };
        var url = STATE.modalMode === 'create' ? urlMap[STATE.modalType].create : urlMap[STATE.modalType].edit(STATE.editId);

        try {
            var result = await ajaxPost(url, payload);
            if (result.ok && result.data.success) {
                closeModal('crud-modal');
                showToast(result.data.message, 'success');
                updateListDOM(STATE.modalType, STATE.modalMode, result.data.item, STATE.editId);
            } else {
                var errors = result.data.errors || {};
                if (errors.__all__ && globalEl) {
                    globalEl.textContent = errors.__all__;
                    globalEl.classList.remove('hidden');
                }
                Object.entries(errors).forEach(function(entry) {
                    if (entry[0] !== '__all__') showFieldError(entry[0], entry[1]);
                });
            }
        } catch(err) {
            if (globalEl) {
                globalEl.textContent = 'Error de conexión. Inténtalo de nuevo.';
                globalEl.classList.remove('hidden');
            }
        } finally {
            setSubmitLoading(false);
        }
    };

    window.openDeleteModal = function(type, id, nombre) {
        STATE.deleteType = type;
        STATE.deleteId = id;
        var labels = { categoria: 'la categoría', familia: 'la familia', tema: 'el tema' };
        var warnings = {
            categoria: 'Esto eliminará también todas las familias, temas y apuntes que dependen de esta categoría.',
            familia: 'Esto eliminará también todos los temas y apuntes que dependen de esta familia.',
            tema: 'Esto eliminará también todos los apuntes que pertenecen a este tema.',
        };
        document.getElementById('delete-modal-name').textContent = labels[type] + ' "' + nombre + '"';
        document.getElementById('delete-modal-warning').textContent = warnings[type];
        setDeleteLoading(false);
        openModal('delete-modal');
    };

    window.executeDelete = async function() {
        setDeleteLoading(true);
        var urlMap = {
            categoria: URLS.categoriaDelete,
            familia: URLS.familiaDelete,
            tema: URLS.temaDelete,
        };
        try {
            var result = await ajaxPost(urlMap[STATE.deleteType](STATE.deleteId), {});
            if (result.ok && result.data.success) {
                closeModal('delete-modal');
                showToast(result.data.message, 'warning');
                removeRowFromList(STATE.deleteType, STATE.deleteId);
            } else {
                showToast('No se pudo eliminar el elemento.', 'error');
            }
        } catch(e) {
            showToast('Error de conexión.', 'error');
        } finally {
            setDeleteLoading(false);
        }
    };

    function setDeleteLoading(loading) {
        var btn = document.getElementById('delete-confirm-btn');
        var icon = document.getElementById('delete-confirm-icon');
        var spinner = document.getElementById('delete-confirm-spinner');
        btn.disabled = loading;
        if (icon) icon.classList.toggle('hidden', loading);
        if (spinner) spinner.classList.toggle('hidden', !loading);
    }

    function openModal(id) {
        var modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        setTimeout(function() {
            var input = modal.querySelector('input[type="text"]');
            if (input) input.focus();
        }, 100);
    }

    window.closeModal = function(id) {
        var modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    };

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal('crud-modal');
            closeModal('delete-modal');
        }
    });

    function updateListDOM(type, mode, item, editId) {
        var prefixMap = { categoria: 'cat', familia: 'fam', tema: 'tema' };
        var prefix = prefixMap[type];
        if (mode === 'edit') {
            var row = document.getElementById(prefix + '-row-' + editId);
            if (row) {
                var nameEl = row.querySelector('p.font-semibold, .font-semibold.text-sm');
                var slugEl = row.querySelector('p.font-mono, .font-mono');
                if (nameEl) nameEl.textContent = item.nombre;
                if (slugEl) slugEl.textContent = item.slug;
            }
        } else {
            var listEl = document.getElementById('list-' + type + 's');
            if (!listEl) return;
            var empty = document.getElementById('empty-' + type + 's');
            if (empty) empty.remove();
            listEl.insertAdjacentHTML('afterbegin', buildRow(type, item));
        }
    }

    function esc(str) {
        return String(str || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
    }

    function buildRow(type, item) {
        if (type === 'categoria') {
            return '<div id="cat-row-' + item.id + '" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-[#1c2028] border border-slate-200 dark:border-darkBorder rounded-xl hover:border-primary-300 dark:hover:border-primary-700 transition-all group">'
                + '<div class="min-w-0">'
                + '<p class="font-semibold text-sm text-slate-900 dark:text-slate-100 truncate">' + esc(item.nombre) + '</p>'
                + '<p class="text-xs text-slate-400 font-mono">' + esc(item.slug) + '</p>'
                + (item.descripcion ? '<p class="text-xs text-slate-500 mt-0.5 truncate max-w-xs">' + esc(item.descripcion) + '</p>' : '')
                + '</div>'
                + '<div class="flex items-center gap-2 flex-shrink-0 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">'
                + '<button onclick="openEditModal(\'categoria\', ' + item.id + ', \'' + esc(item.nombre) + '\', \'' + esc(item.slug) + '\', \'' + esc(item.descripcion || '') + '\')" class="p-1.5 text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-950/30 rounded-lg transition-colors" title="Editar"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg></button>'
                + '<button onclick="openDeleteModal(\'categoria\', ' + item.id + ', \'' + esc(item.nombre) + '\')" class="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors" title="Eliminar"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></button>'
                + '</div></div>';
        } else if (type === 'familia') {
            return '<div id="fam-row-' + item.id + '" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-[#1c2028] border border-slate-200 dark:border-darkBorder rounded-xl hover:border-secondary-300 dark:hover:border-secondary-700 transition-all group">'
                + '<div class="min-w-0">'
                + '<div class="flex items-center gap-2 mb-0.5">'
                + '<span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">' + esc(item.categoria_nombre) + '</span>'
                + '<svg class="w-3 h-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>'
                + '<span class="font-semibold text-sm text-slate-900 dark:text-slate-100">' + esc(item.nombre) + '</span>'
                + '</div>'
                + '<p class="text-xs text-slate-400 font-mono">' + esc(item.slug) + '</p>'
                + '</div>'
                + '<div class="flex items-center gap-2 flex-shrink-0 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">'
                + '<button onclick="openEditModal(\'familia\', ' + item.id + ', \'' + esc(item.nombre) + '\', \'' + esc(item.slug) + '\', \'' + esc(item.descripcion || '') + '\', ' + item.categoria_id + ', \'' + esc(item.categoria_nombre) + '\')" class="p-1.5 text-slate-400 hover:text-secondary-600 dark:hover:text-secondary-400 hover:bg-secondary-50 dark:hover:bg-secondary-950/30 rounded-lg transition-colors" title="Editar"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg></button>'
                + '<button onclick="openDeleteModal(\'familia\', ' + item.id + ', \'' + esc(item.nombre) + '\')" class="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors" title="Eliminar"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></button>'
                + '</div></div>';
        } else {
            return '<div id="tema-row-' + item.id + '" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-[#1c2028] border border-slate-200 dark:border-darkBorder rounded-xl hover:border-amber-300 dark:hover:border-amber-700 transition-all group">'
                + '<div class="min-w-0">'
                + '<div class="flex items-center flex-wrap gap-1.5 mb-0.5">'
                + '<span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">' + esc(item.categoria_nombre) + '</span>'
                + '<svg class="w-3 h-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>'
                + '<span class="text-[10px] font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">' + esc(item.familia_nombre) + '</span>'
                + '<svg class="w-3 h-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>'
                + '<span class="font-semibold text-sm text-slate-900 dark:text-slate-100">' + esc(item.nombre) + '</span>'
                + '</div>'
                + '<p class="text-xs text-slate-400 font-mono">' + esc(item.slug) + '</p>'
                + '</div>'
                + '<div class="flex items-center gap-2 flex-shrink-0 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">'
                + '<button onclick="openEditModal(\'tema\', ' + item.id + ', \'' + esc(item.nombre) + '\', \'' + esc(item.slug) + '\', \'' + esc(item.descripcion || '') + '\', ' + item.familia_id + ', \'' + esc(item.familia_nombre) + '\', 0, \'\')" class="p-1.5 text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/30 rounded-lg transition-colors" title="Editar"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg></button>'
                + '<button onclick="openDeleteModal(\'tema\', ' + item.id + ', \'' + esc(item.nombre) + '\')" class="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors" title="Eliminar"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></button>'
                + '</div></div>';
        }
    }

    function removeRowFromList(type, id) {
        var prefixMap = { categoria: 'cat', familia: 'fam', tema: 'tema' };
        var row = document.getElementById(prefixMap[type] + '-row-' + id);
        if (row) {
            row.style.transition = 'all 0.3s ease-out';
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
            setTimeout(function() { row.remove(); }, 300);
        }
    }

    window.showToast = function(message, type) {
        type = type || 'success';
        var container = document.getElementById('toast-container');
        if (!container) return;
        var id = 'toast-' + Date.now();
        var configs = {
            success: { bg: 'bg-emerald-600', icon: '✓', label: 'Éxito' },
            warning: { bg: 'bg-amber-500', icon: '⚠', label: 'Aviso' },
            error: { bg: 'bg-rose-600', icon: '✕', label: 'Error' },
            info: { bg: 'bg-primary-600', icon: 'ℹ', label: 'Info' },
        };
        var cfg = configs[type] || configs.info;
        var toast = document.createElement('div');
        toast.id = id;
        toast.className = 'pointer-events-auto flex items-start gap-3 ' + cfg.bg + ' text-white px-4 py-3 rounded-xl shadow-2xl max-w-sm w-full transform translate-x-full transition-transform duration-300 ease-out';
        toast.innerHTML = '<span class="text-lg leading-none mt-0.5 flex-shrink-0">' + cfg.icon + '</span>'
            + '<div class="flex-1 min-w-0">'
            + '<p class="text-xs font-bold uppercase tracking-wider opacity-80">' + cfg.label + '</p>'
            + '<p class="text-sm font-medium mt-0.5 leading-snug">' + message + '</p>'
            + '</div>'
            + '<button onclick="document.getElementById(\'' + id + '\').remove()" class="ml-1 text-white/70 hover:text-white flex-shrink-0">'
            + '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>';
        container.appendChild(toast);
        requestAnimationFrame(function() { toast.style.transform = 'translateX(0)'; });
        setTimeout(function() {
            toast.style.transform = 'translateX(calc(100% + 20px))';
            toast.style.opacity = '0';
            setTimeout(function() { toast.remove(); }, 350);
        }, 4000);
    };
})();

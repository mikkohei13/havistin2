(function () {
    function tokenNames(template) {
        var names = [];
        var re = /\{([^}]+)\}/g;
        var m;
        while ((m = re.exec(template)) !== null) {
            if (names.indexOf(m[1]) === -1) {
                names.push(m[1]);
            }
        }
        return names;
    }

    function buildUrl(form, template) {
        var url = template;
        var names = tokenNames(template);
        for (var i = 0; i < names.length; i++) {
            var name = names[i];
            var el = form.elements[name];
            var val = el && el.value != null ? String(el.value) : '';
            url = url.split('{' + name + '}').join(val);
        }
        return url;
    }

    function allFilled(form, template) {
        var names = tokenNames(template);
        for (var i = 0; i < names.length; i++) {
            var el = form.elements[names[i]];
            if (!el || el.value === '' || el.value === null) {
                return false;
            }
        }
        return true;
    }

    function updateSubmit(form, btn, template) {
        btn.disabled = !allFilled(form, template);
    }

    function prefillFromPath(form, template) {
        var path = window.location.pathname.replace(/\/$/, '');
        var segs = path.split('/');

        if (path.indexOf('/my/year/') !== -1 && segs.length >= 5) {
            var y = segs[3];
            var taxon = segs[4];
            if (form.elements.year) {
                form.elements.year.value = y;
            }
            if (form.elements.taxon) {
                form.elements.taxon.value = taxon;
            }
            return;
        }

        if (path.indexOf('/my/documents/') !== -1 && segs.length >= 4) {
            var yd = segs[3];
            if (form.elements.year && /^\d{4}$/.test(yd)) {
                form.elements.year.value = yd;
            }
            return;
        }

        if (path.indexOf('/my/groups/') !== -1 && segs.length >= 5) {
            var yg = segs[3];
            var rank = segs[4] ? segs[4].toLowerCase() : '';
            if (form.elements.year) {
                form.elements.year.value = yg;
            }
            if (form.elements.rank) {
                var opt = form.elements.rank.querySelector('option[value="' + rank + '"]');
                if (opt) {
                    form.elements.rank.value = rank;
                }
            }
            return;
        }

        if (path.indexOf('/talvilinnut/laskenta/') !== -1 && segs.length >= 5) {
            var society = segs[3];
            var seasonSeg = segs[4];
            var dash = seasonSeg.lastIndexOf('-');
            if (dash > 0) {
                var sy = seasonSeg.slice(0, dash);
                var per = seasonSeg.slice(dash + 1);
                if (form.elements.society) {
                    form.elements.society.value = society;
                }
                if (form.elements.year) {
                    form.elements.year.value = sy;
                }
                if (form.elements.period) {
                    form.elements.period.value = per;
                }
            }
            return;
        }

        if (path.indexOf('/stats/observers/species') !== -1) {
            if (segs.length >= 5 && segs[3] === 'species') {
                var ystats = segs[4];
                if (form.elements.year && /^\d{4}$/.test(ystats)) {
                    form.elements.year.value = ystats;
                }
            }
        }
    }

    function wireForm(form) {
        var template = form.getAttribute('data-path-template');
        if (!template) {
            return;
        }
        var btn = form.querySelector('.havistin-path-nav-submit');
        if (!btn) {
            return;
        }
        var busyLabel = form.getAttribute('data-busy-label') || '…';
        var idleLabel = btn.textContent;

        function refresh() {
            updateSubmit(form, btn, template);
        }

        prefillFromPath(form, template);
        refresh();

        form.addEventListener('change', refresh);
        form.addEventListener('input', refresh);

        btn.addEventListener('click', function () {
            if (!allFilled(form, template)) {
                return;
            }
            btn.disabled = true;
            btn.textContent = busyLabel;
            document.body.style.cursor = 'wait';
            window.location.href = buildUrl(form, template);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var forms = document.querySelectorAll('form.havistin-path-nav[data-path-template]');
        for (var i = 0; i < forms.length; i++) {
            wireForm(forms[i]);
        }
    });
})();

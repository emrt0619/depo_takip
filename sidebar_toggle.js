/**
 * Sidebar Toggle Button — Nanomanyetik Depo Takip
 * 
 * Her zaman sol üstte görünen toggle butonu.
 * - Sidebar kapalı → ☰ ikonu → tıklayınca açar
 * - Sidebar açık   → ✕ ikonu → tıklayınca kapatır
 */
(function () {
    var pd = window.parent.document;

    // Tekrar enjekte etme
    if (pd.getElementById('sb-toggle-btn')) return;

    // Eski butonu temizle (varsa)
    var old = pd.getElementById('sb-open-btn');
    if (old) old.remove();

    // ── SVG ikonları ──
    var ICON_OPEN = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
    var ICON_CLOSE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

    // ── Buton oluştur ──
    var btn = pd.createElement('div');
    btn.id = 'sb-toggle-btn';
    btn.title = 'Toggle Sidebar';
    btn.innerHTML = ICON_OPEN;
    btn.style.cssText = [
        'position:fixed',
        'top:14px',
        'left:14px',
        'z-index:999999',
        'width:44px',
        'height:44px',
        'border-radius:12px',
        'border:1.5px solid rgba(0,212,255,0.35)',
        'background:linear-gradient(135deg,rgba(13,18,36,0.97),rgba(16,24,48,0.97))',
        'backdrop-filter:blur(16px)',
        'box-shadow:0 4px 20px rgba(0,0,0,0.5),0 0 12px rgba(0,212,255,0.08)',
        'cursor:pointer',
        'display:flex',
        'align-items:center',
        'justify-content:center',
        'transition:all 0.3s ease',
        'color:#00d4ff',
        'user-select:none'
    ].join(';') + ';';
    pd.body.appendChild(btn);

    // ── Hover stili ──
    var style = pd.createElement('style');
    style.textContent = '#sb-toggle-btn:hover{border-color:#00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.3),0 4px 20px rgba(0,0,0,0.5)!important;transform:scale(1.08);}#sb-toggle-btn:active{transform:scale(0.95)!important;}';
    pd.head.appendChild(style);

    // ── Sidebar durumunu kontrol et ──
    function isSidebarOpen() {
        var sb = pd.querySelector('[data-testid="stSidebar"]');
        if (!sb) return false;
        var ex = sb.getAttribute('aria-expanded');
        if (ex === 'true') return true;
        if (ex === 'false') return false;
        return sb.getBoundingClientRect().width > 50;
    }

    // ── Sidebar'ı AÇ ──
    function openSidebar() {
        // 1) Native collapsedControl
        var cc = pd.querySelector('[data-testid="collapsedControl"]');
        if (cc) { cc.click(); return; }

        // 2) Header'daki sidebar toggle (ana menü hariç)
        var header = pd.querySelector('[data-testid="stHeader"]');
        if (header) {
            var btns = header.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].closest('[data-testid="stMainMenu"]')) continue;
                if (btns[i].getAttribute('data-testid') === 'stMainMenu') continue;
                var rect = btns[i].getBoundingClientRect();
                // Sol taraftaki butonlara odaklan (sidebar toggle sol tarafta olur)
                if (rect.left < 100) {
                    btns[i].click();
                    return;
                }
            }
        }

        // 3) elementFromPoint ile native butonu bul
        var el = pd.elementFromPoint(20, 35);
        if (el) {
            var closest = el.closest('button') || el;
            if (closest.tagName === 'BUTTON' || closest.getAttribute('role') === 'button') {
                closest.click();
                return;
            }
        }

        // 4) Sidebar CSS override (son çare)
        var sb = pd.querySelector('[data-testid="stSidebar"]');
        if (sb) {
            sb.setAttribute('aria-expanded', 'true');
            sb.style.width = '';
            sb.style.transform = '';
        }
    }

    // ── Sidebar'ı KAPAT ──
    function closeSidebar() {
        // 1) Sidebar içindeki kapatma butonu (baseButton-headerNoPadding)
        var sb = pd.querySelector('[data-testid="stSidebar"]');
        if (sb) {
            var closeBtn = sb.querySelector('button[data-testid="baseButton-headerNoPadding"]');
            if (closeBtn) { closeBtn.click(); return; }
            // Herhangi bir kapatma butonu
            var allBtns = sb.querySelectorAll('button');
            for (var i = 0; i < allBtns.length; i++) {
                var r = allBtns[i].getBoundingClientRect();
                // Sidebar üst kısmındaki (y < 50) ve sağ taraftaki butonlar kapatma butonudur
                if (r.top < 60 && r.right > 100) {
                    allBtns[i].click();
                    return;
                }
            }
        }

        // 2) collapsedControl aslında toggle gibi çalışabilir
        var cc = pd.querySelector('[data-testid="collapsedControl"]');
        if (cc) { cc.click(); return; }

        // 3) Header'daki toggle butonu
        var header = pd.querySelector('[data-testid="stHeader"]');
        if (header) {
            var btns = header.querySelectorAll('button');
            for (var j = 0; j < btns.length; j++) {
                if (btns[j].closest('[data-testid="stMainMenu"]')) continue;
                var rect2 = btns[j].getBoundingClientRect();
                if (rect2.left < 100) {
                    btns[j].click();
                    return;
                }
            }
        }

        // 4) Doğrudan CSS ile kapat
        if (sb) {
            sb.setAttribute('aria-expanded', 'false');
        }
    }

    // ── Click handler ──
    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        e.preventDefault();
        if (isSidebarOpen()) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    // ── İkon güncelle (300ms aralıklarla) ──
    function updateIcon() {
        if (isSidebarOpen()) {
            btn.innerHTML = ICON_CLOSE;
            btn.title = 'Sidebar Kapat';
        } else {
            btn.innerHTML = ICON_OPEN;
            btn.title = 'Sidebar Aç';
        }
    }
    setInterval(updateIcon, 300);
    updateIcon();
    // ── Dil butonuna bayrak enjekte et ──
    var UK_FLAG = '<svg viewBox="0 0 60 30" width="22" height="11" style="vertical-align:middle;border-radius:2px;margin-right:6px;flex-shrink:0;box-shadow:0 1px 2px rgba(0,0,0,0.3)"><clipPath id="flg"><rect width="60" height="30"/></clipPath><g clip-path="url(#flg)"><rect width="60" height="30" fill="#012169"/><path d="M0 0L60 30M60 0L0 30" stroke="#fff" stroke-width="6"/><path d="M0 0L60 30M60 0L0 30" stroke="#C8102E" stroke-width="4"/><path d="M30 0V30M0 15H60" stroke="#fff" stroke-width="10"/><path d="M30 0V30M0 15H60" stroke="#C8102E" stroke-width="6"/></g></svg>';
    var TR_FLAG = '<svg viewBox="0 0 60 40" width="22" height="15" style="vertical-align:middle;border-radius:2px;margin-right:6px;flex-shrink:0;box-shadow:0 1px 2px rgba(0,0,0,0.3)"><rect width="60" height="40" fill="#E30A17"/><circle cx="23" cy="20" r="10" fill="#fff"/><circle cx="26" cy="20" r="8" fill="#E30A17"/><polygon points="35,20 29.3,22.2 32,17 28,24 33.5,19" fill="#fff" transform="rotate(18,31,20)"/></svg>';

    function injectFlags() {
        var sidebar = pd.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        var buttons = sidebar.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            var b = buttons[i];
            var txt = (b.textContent || '').replace(/\s+/g, ' ').trim();
            if (txt === 'English' || txt === 'Türkçe') {
                var expectedType = (txt === 'English') ? 'uk' : 'tr';
                var existing = b.querySelector('.lang-flag');
                // Bayrak doğru tipte zaten varsa atla
                if (existing && existing.getAttribute('data-flag') === expectedType) return;
                // Yanlış bayrak varsa kaldır
                if (existing) existing.remove();
                var flag = pd.createElement('span');
                flag.className = 'lang-flag';
                flag.setAttribute('data-flag', expectedType);
                flag.innerHTML = (expectedType === 'uk') ? UK_FLAG : TR_FLAG;
                flag.style.cssText = 'display:inline-flex;align-items:center;';
                b.style.display = 'inline-flex';
                b.style.alignItems = 'center';
                b.style.justifyContent = 'center';
                b.insertBefore(flag, b.firstChild);
            }
        }
    }
    setInterval(injectFlags, 500);
    injectFlags();
})();

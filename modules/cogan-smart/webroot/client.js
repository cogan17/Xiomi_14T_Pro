/* Shared by the independently installable Cogan companions. */
(() => {
  'use strict';
  const T = value => CoganI18n.t(value);
  const text = (id, value) => {
    const el = document.getElementById(id), next = T(String(value));
    if (el && el.textContent !== next) { el.textContent = next; markup.delete(el); }
  };
  const markup = new WeakMap();
  const html = (id, value) => {
    const el = document.getElementById(id);
    if (el && markup.get(el) !== value) { el.innerHTML = value; CoganI18n.apply(el); markup.set(el, value); }
  };
  const shortKernel = release => {
    const value = String(release || ''), version = value.match(/\b6\.1\.\d+\b/);
    if (!version) return 'Kernel ' + (value.match(/^\d+\.\d+\.\d+/)?.[0] || 'tidak diketahui');
    const revision = value.match(/(?:^|[-_])r(\d+)(?:[-_]|$)/i);
    return (/cogan/i.test(value) ? 'Cogan' + (revision ? ' r' + revision[1] : '') : 'GKI') + ' · ' + version[0];
  };
  const quote = value => "'" + String(value).replace(/'/g, "'\\''") + "'";
  // Last answers, kept so a tab shows its last values at once while it reads fresh ones:
  // each tab is its own page, so without this every switch starts empty.
  const store = {
    get(key) { try { return JSON.parse(localStorage.getItem('cogan.cache.v291.' + CoganI18n.language() + '.' + key)); } catch (_) { return null; } },
    set(key, value) { try { localStorage.setItem('cogan.cache.v291.' + CoganI18n.language() + '.' + key, JSON.stringify(value)); } catch (_) { /* storage off or full */ } }
  };

  function create(script) {
    let sequence = 0, running = false, revision = 0;
    const queue = [], reads = new Map();

    function native(args) {
      args = ['--lang', CoganI18n.language(), ...args];
      return new Promise((resolve, reject) => {
        if (typeof ksu === 'undefined') return reject(new Error('Buka dari WebUI root manager'));
        const callback = 'cogan_stream_' + Date.now() + '_' + sequence++;
        const out = [], err = [];
        let settled = false;
        const timeout = setTimeout(() => finish(new Error('Perintah belum selesai; periksa status sebelum mencoba lagi')), 120000);
        function finish(error, errno = 0, stdout = out.join('\n'), stderr = err.join('\n')) {
          if (settled) return;
          settled = true; clearTimeout(timeout);
          // Some managers send an error event immediately after a nonzero exit.
          setTimeout(() => { delete window[callback]; }, 1000);
          if (error) reject(error); else resolve({errno, stdout, stderr});
        }
        const event = (name, data) => {
          if (name === 'exit') finish(null, Number(data));
          else if (name === 'error') finish(new Error(data?.message || String(data || 'Perintah gagal')));
        };
        if (typeof ksu.spawn === 'function') {
          window[callback] = {
            stdout: {emit: (name, data) => { if (!settled && name === 'data') out.push(String(data)); }},
            stderr: {emit: (name, data) => { if (!settled && name === 'data') err.push(String(data)); }},
            emit: event, exit: code => event('exit', code), error: error => event('error', error)
          };
          try {
            // Native managers join arguments into a shell command; quote each one.
            ksu.spawn('sh', JSON.stringify([script, ...args].map(quote)), '{}', callback);
          } catch (error) { finish(error); }
        } else if (typeof ksu.exec === 'function') {
          window[callback] = (errno, stdout, stderr) => finish(null, Number(errno), stdout, stderr);
          try { ksu.exec(['sh', script, ...args].map(quote).join(' '), '{}', callback); }
          catch (error) { finish(error); }
        } else finish(new Error('API shell root manager tidak tersedia'));
      });
    }

    async function pump() {
      if (running || !queue.length) return;
      running = true;
      const job = queue.shift();
      try {
        const result = await native(job.args), command = job.args[0];
        if (result.errno !== 0) throw new Error(`Perintah ${command} gagal (kode ${result.errno}): ${String(result.stderr || 'tanpa keterangan').trim().slice(0, 200)}`);
        let data;
        try { data = JSON.parse(result.stdout); }
        catch (error) { throw new Error(`Respons ${command} bukan JSON lengkap: ${error.message.slice(0, 160)}`); }
        if (!data || typeof data !== 'object') throw new Error(`Respons ${command} tidak valid`);
        if (data.ok === 0 && command !== 'detect') throw new Error(T(data.error || 'Perintah belum berhasil'));
        if (job.read) {
          store.set(script + ' ' + job.key, {at: Date.now(), data});
          // Status answers carry the identity object; 'now' uses a numeric "kernel" for CPU time.
          if (data.kernel && typeof data.kernel === 'object') store.set('identity', {kernel: data.kernel, device: data.device});
        }
        job.resolve(data);
      } catch (error) { job.reject(error); }
      finally {
        if (reads.get(job.key) === job.promise) reads.delete(job.key);
        running = false; pump();
      }
    }

    function report(value, {background = false} = {}) {
      const args = String(value).trim().split(/\s+/), key = args.join(' ');
      if (args.some(arg => !/^[A-Za-z0-9_.-]+$/.test(arg))) return Promise.reject(new Error('Argumen tidak valid'));
      const read = /^(status|live|now|summary|events|cooling|scan|pkgs)$/.test(args[0]);
      if (read && reads.has(key)) return reads.get(key);
      if (!read) revision++;
      let resolve, reject;
      const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
      const job = {args, key, promise, resolve, reject, background, read};
      if (read) reads.set(key, promise);
      if (background) queue.push(job);
      else {
        const firstBackground = queue.findIndex(item => item.background);
        queue.splice(firstBackground < 0 ? queue.length : firstBackground, 0, job);
      }
      // Queue in this turn so a user action can precede pending background work.
      Promise.resolve().then(pump);
      return promise;
    }
    // {at, data} of the last successful read with these arguments, or null.
    const cached = value => store.get(script + ' ' + String(value).trim().split(/\s+/).join(' '));
    return {report, cached, get revision() { return revision; }};
  }

  function poll(task, interval = 5000) {
    let timer, active = false, again = false, stopped = false, suspended = false;
    function schedule(delay) {
      clearTimeout(timer);
      if (!stopped && !suspended && !document.hidden) timer = setTimeout(tick, delay);
    }
    async function tick() {
      if (active) { again = true; return; }
      if (stopped || suspended || document.hidden) return;
      active = true;
      try { await task(); } catch (_) { /* The page displays read errors. */ }
      finally { active = false; schedule(again ? 0 : interval); again = false; }
    }
    const visible = () => document.hidden ? clearTimeout(timer) : schedule(0);
    // A tab can be restored from WebView's back/forward cache. pagehide is a pause,
    // not a permanent stop, otherwise that page can display old values indefinitely.
    const hide = () => { suspended = true; clearTimeout(timer); };
    const show = () => { suspended = false; schedule(0); };
    document.addEventListener('visibilitychange', visible);
    window.addEventListener('pagehide', hide);
    window.addEventListener('pageshow', show);
    const stop = () => {
      stopped = true; clearTimeout(timer);
      document.removeEventListener('visibilitychange', visible);
      window.removeEventListener('pagehide', hide); window.removeEventListener('pageshow', show);
    };
    schedule(0);
    return {poke: () => active ? again = true : schedule(0), stop};
  }

  let actionBusy = false;
  async function action(button, message, task) {
    if (actionBusy) return;
    actionBusy = true;
    const controls = [...document.querySelectorAll('button[data-action]')];
    if (!controls.includes(button)) controls.push(button);
    const disabled = controls.map(control => control.disabled);
    controls.forEach(control => control.disabled = true);
    button.setAttribute('aria-busy', 'true');
    text('actionStatus', message);
    document.getElementById('actionStatus')?.classList.remove('hidden');
    document.getElementById('actionStatus')?.classList.add('working');
    try {
      await new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 0)));
      await task();
    } finally {
      actionBusy = false;
      controls.forEach((control, index) => control.disabled = disabled[index]);
      button.removeAttribute('aria-busy');
      document.getElementById('actionStatus')?.classList.remove('working');
    }
  }
  function kernel(sample, peer, name) {
    if (name) text('peerStatus', name + ': ' + (peer?.installed ? (peer.running ? 'aktif' : 'berhenti') : 'belum terpasang') + (peer?.version ? ' · ' + peer.version : ''));
    const value = sample.kernel;
    if (!value) return;
    text('kernelTitle', shortKernel(value.original || value.release));
    text('bridgeStatus', value.bridge ? 'Bridge native aktif' : value.compat_61 ? 'Kompatibilitas 6.1 · sysfs' : 'Akses sysfs perangkat');
    text('identityLabel', value.verified ? 'Identitas asli · terverifikasi' : 'Identitas dari ' + (value.source === 'uname_only' ? 'uname' : '/proc') + ' · belum terverifikasi');
    text('kernelBadge', value.verified ? '✓ terverifikasi' : 'belum terverifikasi');
    text('originalKernel', value.original || value.release || 'Tidak tersedia');
    text('shownKernel', 'uname: ' + (value.uname || '—') + (value.different ? ' · berbeda dari sumber di atas' : ''));
    text('kernelFeatures', value.features || 'Fitur bawaan belum dikonfirmasi.');
    text('kernelBanner', value.banner || 'Info build tidak tersedia.');
    const client = raw => { const [code, age] = String(raw || '').split(' ').map(Number); return code > 0 ? 'aktif (' + (age || 0) + ' dtk)' : 'belum aktif'; };
    text('clients', value.bridge ? 'Dikenali kernel: Power ' + client(value.power_client) + ' · Thermal ' + client(value.thermal_client) : 'Bridge native memerlukan driver Cogan Bridge dalam build kernel 6.1. Kontrol sysfs tetap mengikuti dukungan perangkat.');
    const d = sample.device;
    if (d) text('deviceStatus', '📱 ' + (d.name || 'Perangkat') + (d.codename ? ' (' + d.codename + (d.platform ? ' · ' + d.platform : '') + ')' : '') + ' · '
      + (d.match === 1 ? (d.verified ? '✓ kernel dibuat untuk HP ini' : '≈ nama kernel menyebut HP ini · belum terverifikasi')
        : d.match === 0 ? '✗ kernel dibuat untuk ' + d.kernel_target : 'kernel belum menyebut perangkat target')
      + (d.supported ? '' : ' · modul belum diuji di HP ini'));
  }
  function cooling(devices) {
    text('coolingTitle', 'Cooling kernel · ' + devices.filter(device => device.state > 0).length + ' aktif');
    text('coolingInfo', devices.length ? devices.map(device => `${device.name}: ${device.state}/${device.max}`).join(' · ') : 'Tidak ada cooling device yang dapat dibaca.');
  }
  // Sections (details.fold) stay open or closed as the user left them, per page.
  function folds() {
    const page = location.pathname.split('/').pop() || 'index.html';
    for (const el of document.querySelectorAll('details.fold[id]')) {
      const key = 'cogan.fold.' + page + '.' + el.id;
      try { const saved = localStorage.getItem(key); if (saved !== null) el.open = saved === '1'; } catch (_) { /* storage off */ }
      el.addEventListener('toggle', () => { try { localStorage.setItem(key, el.open ? '1' : '0'); } catch (_) { /* storage off */ } });
    }
  }
  // Kernel and device as last read by any tab ({kernel, device}), or null.
  const identity = () => store.get('identity');
  function health(monitor) {
    const m = {...monitor};
    m.age = m.ts > 0 ? Math.floor(Date.now() / 1000) - m.ts : -1;
    m.fresh = !!(m.running && m.fresh && m.age >= 0 && m.age <= Math.max(90, (m.interval || 20) * 3));
    return m;
  }
  function recorder(monitor) {
    const m = health(monitor);
    return T(!m.running ? '■ berhenti' : m.stalled ? '⚠ data terlambat' : m.fresh ? '● mencatat' : '◌ menyiapkan sampel');
  }
  // App names for the package names in the temperature log (owner 2026-10-24: a spoofed root manager
  // showed as weonse.bxmfmy.qeomje). KernelSU Next and BakaSU both offer ksu.getPackagesInfo. The names go
  // to the module hex-encoded, because report() takes plain tokens only. At most every 6 hours, or every
  // 10 minutes while the manager has not loaded its app list; without the API the package names stay.
  let labelApi;
  async function learnLabels() {
    if (typeof ksu === 'undefined' || typeof ksu.getPackagesInfo !== 'function') return;
    try { if (Date.now() < Number(localStorage.getItem('cogan.labels.next') || 0)) return; } catch (_) { /* storage off */ }
    labelApi = labelApi || create('/data/adb/modules/cogan_smart/thermal/report.sh');
    const pkgs = await labelApi.report('pkgs', {background: true});
    const info = pkgs.length ? JSON.parse(ksu.getPackagesInfo(JSON.stringify(pkgs))) : [];
    const hex = value => Array.from(new TextEncoder().encode(value), b => b.toString(16).padStart(2, '0')).join('');
    const pairs = info.filter(p => p && !p.error && typeof p.appLabel === 'string' && /^[A-Za-z0-9_.]+$/.test(p.packageName || '')
                                  && p.appLabel.trim() && p.appLabel.trim() !== p.packageName)
      .map(p => [p.packageName, hex(p.appLabel.trim())]).filter(([, h]) => h.length <= 120);
    for (let i = 0; i < pairs.length; i += 15) await labelApi.report(['labels', ...pairs.slice(i, i + 15).flat()].join(' '), {background: true});
    const wait = !pkgs.length || pairs.length ? 6 * 3600e3 : 600e3;
    try { localStorage.setItem('cogan.labels.next', String(Date.now() + wait)); } catch (_) { /* storage off */ }
  }
  window.CoganUI = {create, poll, action, text, html, shortKernel, kernel, cooling, folds, identity, health, recorder, learnLabels};
})();

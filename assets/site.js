// Ogni pagina si apre dall'inizio (salvo link a una sezione con #)
try { if ('scrollRestoration' in history) history.scrollRestoration = 'manual'; } catch (e) {}
if (!location.hash) { window.scrollTo(0, 0); window.addEventListener('load', function () { window.scrollTo(0, 0); }); }

// Menu mobile e sottomenu
(function () {
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Chiudi' : 'Menu';
    });
  }
  document.querySelectorAll('.dd > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var dd = b.parentElement;
      var open = dd.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Modulo richiesta appuntamento
  var form = document.getElementById('form-appuntamento');
  if (!form) return;
  var msg = document.getElementById('form-msg');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.querySelector('.hp input').value) return; // anti-spam
    if (!form.reportValidity()) return;
    var data = new FormData(form);
    var endpoint = form.getAttribute('data-endpoint');
    if (endpoint) {
      // Servizio di invio configurato (es. Formspree)
      fetch(endpoint, { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          msg.hidden = false;
          msg.textContent = 'Richiesta inviata. Ti ricontatteremo al più presto.';
        })
        .catch(function () {
          msg.hidden = false;
          msg.textContent = 'Invio non riuscito. Scrivici a centrocoppiafamiglia@gmail.com o chiama il +39 366 531 7960.';
        });
      return;
    }
    // In attesa del servizio: prepara una email con i dati inseriti
    var body = 'Nome: ' + data.get('nome') + '\nCognome: ' + data.get('cognome') +
      '\nTelefono: ' + data.get('telefono') + '\nEmail: ' + data.get('email') +
      '\nServizio: ' + data.get('servizio') + '\n\nMotivo della richiesta:\n' + data.get('motivo');
    window.location.href = 'mailto:centrocoppiafamiglia@gmail.com?subject=' +
      encodeURIComponent('Richiesta appuntamento – ' + data.get('nome') + ' ' + data.get('cognome')) +
      '&body=' + encodeURIComponent(body);
    msg.hidden = false;
    msg.textContent = 'Si è aperto il tuo programma di posta con la richiesta già compilata: premi Invia per completarla.';
  });
})();

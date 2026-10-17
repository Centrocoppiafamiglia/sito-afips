# Sito AFIPS

Sito statico dell'Associazione per la Formazione e l'Intervento PsicoSociale, pubblicato con GitHub Pages.

## Come modificare un testo
1. Apri il file della pagina nella cartella `src/` (es. `src/contatti.html`).
2. Modifica il testo e salva.
3. Esegui `python3 build.py`: rigenera le pagine nella cartella principale.

Menu, intestazione e piè di pagina si trovano in `build.py`. Colori e caratteri in `assets/style.css`.

## Modulo appuntamenti
In `src/contatti.html` il modulo ha l'attributo `data-endpoint=""`. Inserendo l'indirizzo del servizio di invio (es. Formspree) le richieste arrivano via email; finché è vuoto, il modulo apre una email già compilata.

## Calendario eventi
In `src/eventi.html` inserire nell'attributo `data-src` l'indirizzo di incorporamento del Google Calendar pubblico.

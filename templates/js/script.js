document.addEventListener('DOMContentLoaded', () => {
    // Récupérer la valeur de lumos depuis le stockage local
    let lumos = localStorage.getItem('lumos');
    if (lumos !== null) {
        document.getElementById('lumos').checked = lumos === 'true';
        document.body.style.backgroundColor = lumos === 'true' ? 'hsl(0, 0%, 20%)' : 'hsl(0, 0%, 100%)';
        document.body.style.color = lumos === 'true' ? 'hsl(0, 0%, 100%)' : 'hsl(0, 0%, 0%)';
    }

    document.getElementById('lumos').addEventListener('change', () => {
        lumos = document.getElementById('lumos').checked;
        document.body.style.backgroundColor = lumos ? 'hsl(0, 0%, 20%)' : 'hsl(0, 0%, 100%)';
        document.body.style.color = lumos ? 'hsl(0, 0%, 100%)' : 'hsl(0, 0%, 0%)';
        // Sauvegarder la valeur de lumos dans le stockage local
        localStorage.setItem('lumos', lumos);
    });
});

function changeLang(language) {
    if (language === 'fr') {
        // touts les elements de la page avec lang autre que fr sont cachés
        document.querySelectorAll('[lang]').forEach(element => {
            if (element.getAttribute('lang') !== 'fr') {
                element.style.display = 'none';
            }
        });
    } else if (language === 'en') {
        // touts les elements de la page avec lang autre que en sont cachés
        document.querySelectorAll('[lang]').forEach(element => {
            if (element.getAttribute('lang') !== 'en') {
                element.style.display = 'none';
            }
        });
    }

const lang = document.getElementById('langSelect');
lang.addEventListener('change', () => {
    let langValue = lang.value;
    localStorage.setItem('lang', langValue);
    changeLang(langValue);
});}

document.addEventListener('DOMContentLoaded', () => {
    try {
        lang = localStorage.getItem('lang');
    } catch (e) {
        lang = null;
    }
    if (lang !== null) {
        document.getElementById('langSelect').value = lang;
        changeLang(lang);
        setTimeout(() => {
            changeLang(lang)
        }, 4000);
    } 
    if (lang === null) {
        // Par défaut, on affiche le français
        localStorage.setItem('lang', 'fr');
        changeLang('fr');
        setTimeout(() => {
            changeLang('fr')
        }, 4000);
    }
});

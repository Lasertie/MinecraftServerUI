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
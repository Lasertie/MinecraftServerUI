from werkzeug.security import generate_password_hash
print(generate_password_hash('password'))

### Outils (seulement sur la branche dev) pour génerer les hash de mdp avec la lib affin de pouvoir test
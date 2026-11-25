# Exercice Git / GitHub : premier workflow

Énoncé : https://gist.github.com/bdallard/8bdbdd70f234f94823c0c2cde9515388

Le script de la partie 7 est dans [install.sh](install.sh).

## Partie 1 : installation et configuration

```bash
sudo apt install git          # Linux (sur Windows : Git for Windows)
git --version                 # ex. : git version 2.51.0
git config --global user.name "Mon Nom"
git config --global user.email "mon.email@example.com"
```

## Partie 2 : premier dépôt

```bash
mkdir my-first-repo           # créer le dossier
cd my-first-repo              # entrer dedans
git init                      # initialiser le dépôt Git (crée .git/)
touch readme.txt              # créer le fichier
```

## Partie 3 : premier commit

| Question | Commande |
|---|---|
| Voir l'état du dépôt | `git status` |
| Ajouter `readme.txt` à l'index | `git add readme.txt` |
| Commiter avec le message "Add readme file" | `git commit -m "Add readme file"` |
| Voir l'historique | `git log` |

## Partie 4 : modifications

```bash
echo "Second line" >> readme.txt
git status
```

`git status` indique que `readme.txt` est **modifié mais pas indexé** (« Changes not staged for commit ») : Git voit la différence avec le dernier commit, mais elle n'est pas encore prête à être commitée.

```bash
git add readme.txt
git commit -m "Add second line to readme"
```

Il y a maintenant **2 commits** (`git log --oneline` affiche 2 lignes).

## Partie 5 : exploration

- `git diff` montre les différences ligne par ligne entre le répertoire de travail et l'index (lignes ajoutées en `+`, supprimées en `-`). Après un `git add`, il faut `git diff --staged`.
- `git log --oneline` affiche l'historique en version compacte, une ligne par commit : le hash abrégé et le message.

## Partie 6 : branches

```bash
git branch                    # lister les branches (* = branche courante)
git branch feature-script     # créer feature-script
git switch feature-script     # y aller (ou : git checkout feature-script)
git switch -c dev             # créer dev et y aller en une commande (ou : git checkout -b dev)
git switch feature-script     # revenir sur feature-script
git branch --show-current     # vérifier → feature-script
```

## Partie 7 : script Bash sur une branche

```bash
# sur feature-script
nano install.sh               # contenu : voir install.sh
chmod +x install.sh           # le rendre exécutable
git add install.sh
git commit -m "Add install script"
git log --oneline             # 3 commits sur feature-script
```

## Partie 8 : fusion (merge)

```bash
git switch main
ls                            # → readme.txt seulement
```

`install.sh` **n'est pas présent** sur `main`, car il a été commité uniquement sur `feature-script`. Chaque branche a son propre historique.

```bash
git merge feature-script      # fusionner feature-script dans main (ici un « fast-forward »)
ls                            # → install.sh + readme.txt
```

Après la fusion, `install.sh` apparaît dans `main`. `git log --oneline --graph` montre que `main` contient maintenant le commit "Add install script".

```bash
git branch -d feature-script  # supprimer la branche fusionnée
```

## Partie 9 : push vers GitHub

1. Sur GitHub : **New repository** → nom `my-first-repo`, sans README.
2. Relier le dépôt local à GitHub, puis pousser :

```bash
git remote add origin https://github.com/<user>/my-first-repo.git
git push -u origin main
```

3. Après un rafraîchissement, la page GitHub affiche les fichiers `readme.txt` et `install.sh`, ainsi que les commits de l'historique.

## Partie 10 : supprimer et cloner

```bash
cd ..                         # sortir du projet
rm -rf my-first-repo          # supprimer le dossier local
git clone https://github.com/<user>/my-first-repo.git
cd my-first-repo
ls                            # les fichiers sont revenus
git log --oneline             # l'historique aussi
```

## Partie 11 : workflow complet depuis zéro

```bash
# 1. Nettoyage : supprimer le dossier local + le dépôt GitHub (Settings → Delete this repository)
rm -rf my-first-repo

# 2. Nouveau projet
mkdir bash-installer && cd bash-installer
git init
printf "# bash-installer\n\nScript Bash qui installe des paquets automatiquement.\n" > README.md
git add README.md
git commit -m "Add README"

# 3. Branche de fonctionnalité
git switch -c feature-install
cp ../install.sh .            # le script de la partie 7
chmod +x install.sh
git add install.sh
git commit -m "Add install script"

# 4. Fusion et nettoyage
git switch main
git merge feature-install
git branch -d feature-install

# 5. Nouveau dépôt GitHub "bash-installer" (sans README), puis :
git remote add origin https://github.com/<user>/bash-installer.git
git push -u origin main
```

## Questions de réflexion

1. **Pourquoi utiliser un gestionnaire de versions ?** Pour garder l'historique de toutes les modifications, revenir en arrière en cas d'erreur, savoir qui a changé quoi et pourquoi, travailler à plusieurs sans s'écraser, et sauvegarder le code sur un serveur distant.
2. **Différence entre staging et commit ?** Le *staging* (`git add`) prépare les changements à inclure : c'est une zone tampon où l'on choisit précisément ce qui ira dans le prochain commit. Le *commit* (`git commit`) enregistre définitivement cet instantané dans l'historique, avec un message.
3. **Quand faire un commit ?** À chaque unité logique de travail terminée et fonctionnelle : une fonctionnalité, une correction de bug, une étape. Des petits commits fréquents et cohérents valent mieux qu'un énorme commit fourre-tout.
4. **`git init` vs `git clone` ?** `git init` crée un nouveau dépôt vide en local. `git clone` copie un dépôt existant (distant), avec tout son historique, et configure automatiquement le remote `origin`.
5. **Pourquoi de bons messages de commit ?** Pour comprendre l'historique plus tard (soi-même ou les collègues), retrouver facilement quand et pourquoi un changement a été fait, et faciliter les revues de code et le débogage (`git log`, `git blame`, `git bisect`).
6. **À quoi servent les branches ?** À développer une fonctionnalité ou une correction de façon isolée, sans casser la branche principale, puis à l'intégrer par un merge une fois terminée et testée. Elles permettent aussi de travailler en parallèle.
7. **Quand créer une branche plutôt que travailler sur main ?** Dès qu'on développe une nouvelle fonctionnalité, une correction ou une expérimentation, et surtout en équipe. `main` doit rester stable et déployable. On ne travaille directement sur `main` que pour des changements triviaux sur un projet personnel.

# Quartz v4

> “[One] who works with the door open gets all kinds of interruptions, but [they] also occasionally gets clues as to what the world is and what might be important.” — Richard Hamming

Quartz is a set of tools that helps you publish your [digital garden](https://jzhao.xyz/posts/networked-thought) and notes as a website for free.
Quartz v4 features a from-the-ground rewrite focusing on end-user extensibility and ease-of-use.

🔗 Read the documentation and get started: https://quartz.jzhao.xyz/

[Join the Discord Community](https://discord.gg/cRFFHYye7t)

## Déploiement sur Cloudflare Pages

Ce dépôt est prêt pour un déploiement automatique sur [Cloudflare Pages](https://pages.cloudflare.com/).

### Étapes principales :

1. Forkez ou clonez ce dépôt sur GitHub.
2. Configurez les secrets `CLOUDFLARE_API_TOKEN` et `CLOUDFLARE_ACCOUNT_ID` dans les paramètres du dépôt GitHub (Settings > Secrets and variables > Actions).
3. Poussez vos modifications sur la branche `main`.
4. Le workflow GitHub Actions (`.github/workflows/deploy.yml`) va automatiquement builder et déployer le site sur Cloudflare Pages.

### Commandes utiles

- Installer les dépendances :
  ```bash
  npm ci
  ```
- Builder le site :
  ```bash
  npm run build
  ```
- Dossier de sortie (output) : `public/`

Pour plus d'informations, consultez la documentation officielle ou le fichier `docs/hosting.md`.

## Sponsors

<p align="center">
  <a href="https://github.com/sponsors/jackyzha0">
    <img src="https://cdn.jsdelivr.net/gh/jackyzha0/jackyzha0/sponsorkit/sponsors.svg" />
  </a>
</p>

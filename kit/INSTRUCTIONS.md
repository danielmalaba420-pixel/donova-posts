# Procédure de publication automatique — Instagram Donova (@donova.420)

Donova est l'agence de communication digitale de Daniel Malaba à Kinshasa.
Tout est en français. Le nom s'écrit toujours **Donova** (jamais « Danova »).
Daniel a demandé que les posts du matin et du soir soient publiés DIRECTEMENT,
sans validation préalable.

## Règles fixes

- Format : carrousel de **3 à 5 slides**, 1080×1350 (4:5), JPEG, rendu avec `kit/render.py`.
- Le logo Donova est ajouté automatiquement en bas de chaque slide par le script.
- **Dernière slide = type `cta`** : la leçon marketing + appel à écrire en DM à Donova.
- Toujours une **légende + hashtags** (8 à 14 hashtags, dont #Donova #Kinshasa #RDC).
- **Faits vérifiés** : pour « Le saviez-vous ? », vérifier chaque chiffre, date et nom
  par une recherche web (au moins une source fiable). Si un fait ne se confirme pas,
  prendre le sujet suivant.
- **Photos** : uniquement de vraies photos Unsplash (outil Unsplash `search_photos` puis
  `download_asset`), avec le crédit « Photo : Prénom Nom / Unsplash » sur la slide.
  Ne jamais redessiner un logo de marque. Pas de photo de personnalité publique.
  Pas la même photo dans deux posts.
- Ton : simple, direct, accrocheur, tutoiement.

## Étapes

1. Ouvrir `kit/sujets.md`, prendre le premier sujet non coché de la rubrique du créneau
   (matin = « Conseil du jour », soir = « Le saviez-vous ? »).
2. Écrire le contenu, chercher 1 à 2 photos Unsplash et les télécharger dans le
   dossier du post : `AAAA-MM-JJ-matin-<mot-cle>/` ou `AAAA-MM-JJ-soir-<mot-cle>/`.
3. Écrire `post.json` dans ce dossier (modèle : `kit/exemple-post.json`), puis lancer
   `python3 kit/render.py <dossier>`. Regarder chaque slide (lecture de l'image) :
   texte qui ne déborde pas, rien de coupé, logo présent. Corriger et relancer si besoin.
4. Écrire la légende dans `<dossier>/legende.txt`.
5. Cocher le sujet dans `kit/sujets.md` avec la date.
6. Commit + push sur `main` (supprimer les photos sources de plus de 8 Mo s'il y en a).
7. Vérifier que chaque image répond 200 en `image/jpeg` à
   `https://raw.githubusercontent.com/danielmalaba420-pixel/donova-posts/main/<dossier>/slide-N.jpg`
   (attendre 30 s et réessayer si besoin).
8. Publier avec Windsor : connecteur `instagram`, compte `17841479998489027` (donova.420),
   action `create_carousel_post`, `image_urls` dans l'ordre, `caption` = la légende.
9. Envoyer à Daniel un court message : sujet publié, aperçu des slides, lien vers le post si disponible.

En cas de blocage (push refusé, Windsor en erreur, compte déconnecté) : ne pas publier
à moitié. Envoyer à Daniel un message clair qui dit ce qui bloque et ce qu'il doit faire.

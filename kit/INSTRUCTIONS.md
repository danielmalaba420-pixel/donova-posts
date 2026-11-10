# Procédure de publication automatique — Instagram Donova (@donova.420)

Donova est l'agence de communication digitale de Daniel Malaba à Kinshasa.
Tout est en français. Le nom s'écrit toujours **Donova** (jamais « Danova »).
Daniel a demandé que les posts du matin, du midi et du soir soient publiés DIRECTEMENT,
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

## Rubrique Midi (12h47) — « Marketing drôle · Kinshasa »

Demandé par Daniel : « au 21e siècle le marketing doit être plus drôle ». Un post par jour,
centré sur la vie de Kinshasa et des marques d'ici, avec des mots de **lingala**.

- Tag de la slide 1 : « Marketing drôle ». Sujet = premier non coché de la rubrique Midi de
  `kit/sujets.md` (le cocher avec la date après publication).
- Format : 3 à 5 slides sans photo obligatoire (slides `text` / `tips` / `cta` ; une photo
  Unsplash seulement si elle aide la blague). Slide 1 = `text` avec un gros mot/emoji (`big`)
  et un titre qui donne envie de swiper. Dernière slide = `cta` avec une chute drôle + appel à
  écrire à Donova (garder le ton léger).
- Humour : situations du quotidien (clients, prix « en inbox », pannes de réseau, likes de la
  famille, pubs « qui vont buzzer »). On se moque de **situations**, jamais de personnes.
  INTERDIT : politique, tribalisme/ethnies, religion, handicap, personnes réelles, marques
  réelles tournées en ridicule.
- **Tendances de Kinshasa** (demandé par Daniel) : avant de choisir le sujet, chercher sur le web
  ce qui buzze à Kinshasa / en RDC (phénomènes viraux, mèmes, expressions du moment). Si une
  tendance légère s'y prête, elle passe AVANT la liste de `sujets.md` (le sujet de la liste reste
  non coché). On s'inspire de la tendance ; on ne reproduit JAMAIS la photo ou la vidéo d'une
  personne réelle, ni une caricature reconnaissable d'un particulier filmé dans un incident.
  Les dessins sont des personnages ORIGINAUX inventés (outil d'image de Canva ou ElevenLabs si
  disponible, sinon slides texte). Pas d'accusation (police, corruption, politique) : on rit
  de la situation, pas des personnes. Aucune tendance sûre ? Prendre le sujet de la liste.
- Lingala : seulement des mots et expressions courants dont on est SÛR (ex. mbote, malamu,
  kitoko, mbongo, mayele, makambo, likambo te, kobanga te, ndeko, mokolo mosusu, mingi, moke,
  biso, bino, ya solo). Toujours donner la traduction entre parenthèses la première fois.
  En cas de doute sur un mot : ne pas l'utiliser. Mélange français + lingala comme à Kinshasa.
- Légende : 1 phrase drôle + question qui pousse à commenter (« Et toi, tu es quel type de
  client ? ») + invitation à taguer un ami + hashtags (dont #Donova #Kinshasa #RDC #Lingala
  #HumourCongolais #MarketingDrole).
- Pas de fait à vérifier ici, mais aucune statistique inventée.

## Étapes

1. Ouvrir `kit/sujets.md`.
   - Matin = « Actu du digital » : chercher une nouveauté des 7 derniers jours, vérifiée par
     une source fiable, jamais déjà publiée (voir la liste). Ton informatif : ce qui change,
     pour qui, depuis quand, ce que ça veut dire pour une marque à Kinshasa. Pas de leçon.
     Slide 1 = tag « Actu du digital » + titre accrocheur ; slides suivantes = les faits ;
     dernière slide `cta` = « Ce qu'il faut retenir » + appel à écrire à Donova.
     Mentionner la source (nom du média ou de l'entreprise) sur une slide.
   - Midi = « Marketing drôle · Kinshasa » : voir la rubrique Midi ci-dessus.
   - Soir = « Le saviez-vous ? » : premier sujet non coché de la rubrique Soir.
2. Écrire le contenu, chercher 1 à 2 photos Unsplash et les télécharger dans le
   dossier du post : `AAAA-MM-JJ-matin-<mot-cle>/` ou `AAAA-MM-JJ-soir-<mot-cle>/`.
3. Écrire `post.json` dans ce dossier (modèle : `kit/exemple-post.json`), puis lancer
   `python3 kit/render.py <dossier>`. Regarder chaque slide (lecture de l'image) :
   texte qui ne déborde pas, rien de coupé, logo présent. Corriger et relancer si besoin.
4. Écrire la légende dans `<dossier>/legende.txt`.
5. Dans `kit/sujets.md` : cocher le sujet du soir avec la date, ou ajouter l'actu du matin
   à la liste « Actus déjà publiées » (`- AAAA-MM-JJ — titre — source`).
6. Commit + push sur `main` (supprimer les photos sources de plus de 8 Mo s'il y en a).
   Si le push est refusé (un autre post vient d'être poussé) : `git pull --rebase` puis
   repousser — ne jamais abandonner pour ça.
7. Vérifier que chaque image répond 200 en `image/jpeg` à
   `https://raw.githubusercontent.com/danielmalaba420-pixel/donova-posts/main/<dossier>/slide-N.jpg`
   (attendre 30 s et réessayer si besoin).
8. Publier avec Windsor : connecteur `instagram`, compte `17841479998489027` (donova.420),
   action `create_carousel_post`, `image_urls` dans l'ordre, `caption` = la légende.
9. Envoyer à Daniel un court message : sujet publié, aperçu des slides, lien vers le post si disponible.

En cas de blocage (push refusé, Windsor en erreur, compte déconnecté) : ne pas publier
à moitié. Envoyer à Daniel un message clair qui dit ce qui bloque et ce qu'il doit faire.
